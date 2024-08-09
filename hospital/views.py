from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from hospital.models import Hospital,HospitalAdmin,Doctor
from doctor.models import *
from .models import *
from django.urls import reverse
from django.db.models import Q
import json
from django.http import JsonResponse
from .forms import AddHospitalForm,AddDoctorForm
from django.contrib.auth.decorators import login_required
from userSystem.forms import CustomUserProfileForm
from django.db import IntegrityError
from userSystem.views import generate_user_report,patient_list, doctor_list, generate_pdf_view,generate_doctor_pdf_view, generate_doctor_report
from .forms import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django import template


register = template.Library()

@register.simple_tag
def get_hospital_name(hospital_id):
    try:
        hospital = Hospital.objects.get(id=hospital_id)
        return hospital.name
    except Hospital.DoesNotExist:
        return 'Hospital Not Found'

def delete_selected_wards(request, hospital_id):
    if request.method == 'POST':
        hospital = Hospital.objects.get(pk=hospital_id)
        ward_ids_to_delete = request.POST.getlist('delete_wards')

        if ward_ids_to_delete:
            # Delete selected wards
            for ward_id in ward_ids_to_delete:
                ward = Ward.objects.get(pk=ward_id)
                hospital.wards.remove(ward)

            messages.success(request, 'Selected wards deleted successfully.')
        else:
            messages.warning(request, 'No wards selected to delete.')

    return redirect('hospitalview', getname=hospital.name)


@login_required
def vacate_bed(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, patient=request.user)
    booking.state = 'vacant'
    booking.save()
    return redirect('dashboard')  # Redirect to user's dashboard or appropriate page

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, patient=request.user)
    booking.delete()
    return redirect('dashboard')  # Redirect to user's dashboard or appropriate page


@login_required(login_url='UserLogin')
def hospitalview(request, getname):
    hospital = get_object_or_404(Hospital, name=getname)
    
    doctorID = DoctorList.objects.filter(hospitalName_id=hospital.id).values('id', 'doctorName_id', 'is_active')
    doctorData = []
    activedoctorNo = 0

    for i in doctorID:
        eachUserID = Doctor.objects.values_list('userID_id', flat=True).get(id=i['doctorName_id'])
        doctorName = CustomUser.objects.values_list('first_name', flat=True).get(id=eachUserID)
        doctorData.append({'doctorName': doctorName, 'is_active': i['is_active'], 'doctorlistToken': i['id']})
        if i['is_active']:
            activedoctorNo += 1

    listIDs = List.objects.filter(hospital_id=hospital.id).values('id')
    COMPLETEDVS = DELETEDVS = PENDINGVS = 0

    for i in listIDs:
        COMPLETEDVS += BookingPatient.objects.filter(lists_id=i['id'], state='COMPLETED').count()
        DELETEDVS += BookingPatient.objects.filter(lists_id=i['id'], state='DELETED').count()
        PENDINGVS += BookingPatient.objects.filter(lists_id=i['id'], state='PENDING').count()
    
    # Get wards that are either assigned to this hospital or not assigned to any hospital
    all_wards = Ward.objects.filter(Q(hospital__isnull=True) | Q(hospital=hospital))

    context = {
        'hospital': hospital,
        'doctorData': doctorData,
        'activedoctorNo': activedoctorNo,
        'COMPLETEDVS': COMPLETEDVS,
        'DELETEDVS': DELETEDVS,
        'PENDINGVS': PENDINGVS,
        'all_wards': all_wards
    }
    
    return render(request, 'hospitalApp/hospitalDetails.html', context)



def move_and_remove_wards(request, hospital_id):
    if request.method == 'POST':
        hospital = get_object_or_404(Hospital, pk=hospital_id)
        wards_to_move = request.POST.getlist('wards')

        for ward_id in wards_to_move:
            ward = get_object_or_404(Ward, pk=ward_id)
            hospital.wards.add(ward)
            ward.status = 1
            ward.save()

        return redirect('hospitalview', getname=hospital.name)
    else:
        # Get wards not assigned to any hospital
        unassigned_wards = Ward.objects.filter(hospital__isnull=True)
        context = {
            'hospital_id': hospital_id,
            'unassigned_wards': unassigned_wards,
        }
        return redirect('hospitalview', getname=hospital.name)


def delete_selected_beds(request):
    import json
    data = json.loads(request.body)
    bed_ids = data.get('bed_ids', [])

    # Perform deletion of beds
    deleted_count, _ = Bed.objects.filter(id__in=bed_ids).delete()

    # Return JSON response indicating success or failure
    return JsonResponse({'deleted_count': deleted_count})



def hospital_details(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == 'POST':
        form = AssignWardsForm(request.POST, hospital=hospital)
        if form.is_valid():
            for ward in form.cleaned_data['wards']:
                hospital.wards.add(ward)
            return redirect('hospitalview', getname=hospital.name)
    else:
        form = AssignWardsForm(hospital=hospital)
    
    context = {
        'hospital': hospital,
        'form': form,
        'all_wards': Ward.objects.all()
    }
    return redirect('hospitalview', getname=hospital.name)

def assign_wards(request, hospital_id):
    hospital = get_object_or_404(Hospital, pk=hospital_id)
    all_wards = Ward.objects.filter(hospital__isnull=True)  # Fetch wards not assigned to any hospital
    
    # Exclude wards already assigned to the hospital
    assigned_wards_ids = hospital.wards.all().values_list('id', flat=True)
    all_wards = all_wards.exclude(id__in=assigned_wards_ids)

    if request.method == 'POST':
        form = AssignWardsForm(request.POST, hospital=hospital)
        if form.is_valid():
            wards_to_assign = form.cleaned_data.get('wards')
            for ward in wards_to_assign:
                hospital.wards.add(ward)
            hospital.save()
            messages.success(request, 'Wards assigned successfully!')
            return redirect('hospitalview', getname=hospital.name)
        else:
            messages.error(request, 'Form is not valid. Please check the selected wards.')
    else:
        form = AssignWardsForm(hospital=hospital)

    context = {
        'hospital': hospital,
        'all_wards': all_wards,
        'form': form,
    }
    return redirect('hospitalview', getname=hospital.name)


def assign_ward_to_hospital(request):
    if request.method == 'GET':
        ward_id = request.GET.get('ward_id')
        ward = get_object_or_404(Ward, pk=ward_id)
        hospitals = Hospital.objects.all()
        return render(request, 'hospitalApp/assign_ward_to_hospital.html', {'ward': ward, 'hospitals': hospitals})
    
    elif request.method == 'POST':
        ward_id = request.POST.get('ward_id')
        hospital_id = request.POST.get('hospital')
        
        ward = get_object_or_404(Ward, pk=ward_id)
        hospital = get_object_or_404(Hospital, pk=hospital_id)
        
        ward.hospital = hospital
        ward.save()
        
        messages.success(request, f'Ward "{ward.name}" assigned to hospital "{hospital.name}" successfully!')
        return redirect('ward_list')
    

def update_ward(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == "POST":
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            return redirect('ward_list')
    else:
        form = WardForm(instance=ward)
    return redirect('hospitalview', getname=Hospital.name)

def delete_ward(request, pk):
    ward = get_object_or_404(Ward, pk=pk)
    if request.method == "POST":
        ward.delete()
        return redirect('ward_list')
    return redirect('hospitalview', getname=Hospital.name)





def add_ward(request):
    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            ward = form.save(commit=False)
            hospital_id = request.POST.get('hospital_id')

            if hospital_id:
                hospital = get_object_or_404(Hospital, pk=hospital_id)
                ward.hospital = hospital
            ward.save()

            return redirect('ward_list')  # Adjust the URL name as needed
        else:
            print('Form is not valid:', form.errors)  # Debugging line
    else:
        form = WardForm()

    return render(request, 'hospitalApp/ward_form.html', {'form': form})




def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect('bed_bookings', booking_id=booking.pk)
    else:
        form = BookingForm()
    
    # Get patients based on the selected ward in the form
    patients = []
    if 'ward' in request.GET:
        ward_id = request.GET.get('ward')
        patients = Patient.objects.filter(bookings__ward_id=ward_id).distinct().order_by('userID__username')

    return render(request, 'hospitalApp/book_bed.html', {'form': form, 'patients': patients})


def book_bed(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect('bed_bookings', booking_id=booking.pk)
    else:
        form = BookingForm()

    # Get patients based on the selected ward in the form
    patients = []
    if 'ward' in request.GET:
        ward_id = request.GET.get('ward')
        patients = Patient.objects.filter(bookings__ward_id=ward_id).distinct().order_by('userID__username')

    return render(request, 'hospitalApp/book_bed.html', {'form': form, 'patients': patients})

def bed_bookings(request):
    bookings = Booking.objects.all()  # Fetch all bed bookings
    return render(request, 'hospitalApp/bed_bookings.html', {'bookings': bookings})

def ajax_load_wards(request):
    hospital_id = request.GET.get('hospital_id')
    wards = Ward.objects.filter(hospital_id=hospital_id).order_by('name')
    options = [{'id': ward.id, 'name': ward.name} for ward in wards]
    return JsonResponse({'options': options})

def ajax_load_beds(request):
    ward_id = request.GET.get('ward_id')
    beds = Bed.objects.filter(ward_id=ward_id).order_by('id')
    options = [{'id': bed.id, 'name': str(bed.id)} for bed in beds]
    return JsonResponse({'options': options})

def ajax_load_patients(request):
    ward_id = request.GET.get('ward_id')
    patients = Patient.objects.filter(bookings__ward_id=ward_id).distinct().order_by('userID__username')
    options = [{'id': patient.id, 'name': str(patient.userID.username)} for patient in patients]
    return JsonResponse({'options': options})

def get_beds_for_ward(request):
    ward_id = request.GET.get('ward_id')
    if ward_id:
        try:
            ward = Ward.objects.get(id=ward_id)
            beds = Bed.objects.filter(ward=ward).values_list('id', 'bed_number')
            bed_choices = {bed[0]: bed[1] for bed in beds}
            return JsonResponse({'beds': bed_choices})
        except Ward.DoesNotExist:
            return JsonResponse({'error': 'Ward not found.'}, status=404)
    return JsonResponse({'beds': []})  # Return empty list if no ward ID provided


def reserve_bed(request):
    if request.method == 'POST':
        ward_id = request.POST.get('ward_id')
        ward = Ward.objects.get(pk=ward_id)
        # Check if there are available beds or handle logic for reservation
        if ward.beds_remaining > 0:
            # Assuming BookingForm is your form for reservation
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.ward = ward
                booking.state = 'reserved'  # Set the state as reserved
                booking.save()
                messages.success(request, 'Bed reserved successfully!')
                return redirect('ward_list')  # Redirect to ward list or any appropriate view
        else:
            messages.error(request, 'No beds available for reservation.')
            return redirect('ward_list')  # Redirect to ward list or handle as needed
    
    # Handle GET request or invalid form submission
    return redirect('ward_list')  # Redirect to ward list or handle as needed



def approve_bed(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = ApproveBedForm(request.POST, instance=booking)
        if form.is_valid():
            booking.state = 'occupied'
            booking.save()
            return redirect('ward_list')  # Adjust the URL name as needed
    else:
        form = ApproveBedForm(instance=booking)

    context = {'form': form}
    return render(request, 'hospitalApp/approve_bed.html', context)

def delete_reservation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    return redirect('ward_list')  # Adjust the URL name as needed


def add_beds_to_ward(request):
    hospital = Hospital.objects.first()  # Example query to get the first hospital

    if request.method == 'POST':
        form = AddBedsForm(request.POST)
        if form.is_valid():
            ward = form.cleaned_data['ward']
            bed_numbers = form.cleaned_data['bed_numbers']
            for bed_number in bed_numbers.split(','):
                Bed.objects.create(ward=ward, bed_number=bed_number.strip())

            return redirect('ward_list')  # Adjust the URL name as needed

        bed_ids = request.POST.getlist('delete_beds')
        if bed_ids:
            beds_to_delete = Bed.objects.filter(id__in=bed_ids)
            for bed in beds_to_delete:
                bed.delete()

            return redirect('ward_list')  # Adjust the URL name as needed
    else:
        form = AddBedsForm()

    context = {
        'hospital': hospital,
        'form': form,
    }
    return render(request, 'hospitalApp/add_beds_to_ward.html', context)


def add_bed_to_ward(request, ward_id):
    # Fetch the ward object
    ward = get_object_or_404(Ward, pk=ward_id)

    if request.method == 'POST':
        if 'add_bed' in request.POST:
            # Handle the addition of a new bed
            bed_number = request.POST.get('bed_number')
            if bed_number:
                new_bed = Bed.objects.create(ward=ward, bed_number=bed_number)
                new_bed.save()
                return redirect('add-bed-to-ward', ward_id=ward_id)
            
        elif 'delete_beds' in request.POST:
            # Handle the deletion of beds
            bed_ids = request.POST.getlist('delete_beds')
            if bed_ids:
                beds_to_delete = Bed.objects.filter(id__in=bed_ids)
                for bed in beds_to_delete:
                    bed.delete()
                return redirect('ward_list')  # Adjust the URL name as needed

    # Render the template with the form and context
    context = {
        'ward': ward,  # Pass your ward object here
        'beds': Bed.objects.filter(ward=ward),  # Fetch and pass the beds of this ward
    }
    return render(request, 'hospitalApp/add_bed_to_ward.html', context)


def ward_list(request):
    wards = Ward.objects.all()  # Query all wards or as needed
    context = {
        'wards': wards,
    }
    return render(request, 'hospitalApp/ward_list.html', context)


def update_row_numbers(wards):
    # Calculate and populate row numbers for the wards
    for index, ward in enumerate(wards, start=1):
        ward['row_number'] = index
    return wards


def print_wards_report(request):
    wards = Ward.objects.all()
    return render(request, 'hospitalApp/print_wards_report.html', {'wards': wards})

# def homeHospital(request):

#        hosAdminData = list(HospitalAdmin.objects.filter(userID_id=request.user.id).values('id','is_active'))  
#        for i in hosAdminData:
#               if(i['is_active']):
#                      #getting valid hospital admin id
#                      hosAdminId=i['id']
       
#        hospitalData = list(Hospital.objects.filter(createdBy=hosAdminId).values('id','name','hos_type','district','status'))  

#        context={'hospitalData':hospitalData}

#        return render(request, "hospitalApp/home.html",context)

def homeHospital(request):
    # Get the hospital admin data for the logged-in user
    hosAdminData = HospitalAdmin.objects.filter(userID_id=request.user.id, is_active=True).first()

    if hosAdminData:
        hosAdminId = hosAdminData.id
        hospitalData = Hospital.objects.filter(createdBy=hosAdminId).values('id', 'name', 'hos_type', 'district', 'status')
        context = {
            'hospital_id': hosAdminId,  # Pass the hospital admin ID to the context
            'hospitalData': hospitalData,
        }
        return render(request, "hospitalApp/home.html", context)
    else:
        # Handle the case where the logged-in user is not a valid hospital admin
        # For example, redirect to a different page or show an error message
        return HttpResponse("You are not authorized to access this page.")


#add new hospital
def addHospital(request): 
    if request.method == "POST":
       form = AddHospitalForm(request.POST)
       createdID=HospitalAdmin.objects.values_list('id', flat=True).get(userID_id=request.user.id)
       if form.is_valid():
              obj = form.save(commit=False)
              obj.createdBy_id = createdID
              obj.save()
              return redirect("homeHospital")
       else:  
              context={'form':form}
              return render(request, 'hospitalApp/addHospital.html',context)
    else:
       #Add new hospital
       form = AddHospitalForm()
       context={'form':form}
       return render(request, 'hospitalApp/addHospital.html',context)

#add new doctor
def addDoctor(request,id): 
    if request.method == "POST":
       form = AddDoctorForm(request.POST)

       if form.is_valid():
        try: 
              doctorID = form['doctor'].value()
              obj = form.save(commit=False)
              obj.hospital_id = id
              obj.save() 
        except IntegrityError as e:
              context={'form':form , 'excerror':"Same combination already added"}
              return render(request, 'hospitalApp/addDoctor.html',context)
        try:
              #saving to doctor list table
              DoctorList.objects.create(doctorName_id=doctorID,hospitalName_id=id)
              return redirect("homeHospital")
        except IntegrityError as e:
              return redirect("homeHospital")
       else:  
              context={'form':form}
              return render(request, 'hospitalApp/addDoctor.html',context)
    else:
       #Add new doctor
       form = AddDoctorForm()
       context={'form':form}
       return render(request, 'hospitalApp/addDoctor.html',context)




#delete hospital
@login_required(login_url='UserLogin')
def hospitalDelete(request,id ):
       Hospital.objects.get(id=id).delete()
       return redirect("homeHospital")


#Doctor Profile 
#Redirect unauthorized user's from accessing 
@login_required(login_url='UserLogin')
def hosadminMyProfile(request):


    #profile pic
    formset = CustomUserProfileForm()
    context={'formset':formset,}

    return render(request, 'hospitalApp/profile.html',context)

#user pro pic
def uploadHosAdminPropic(request,id):
        if request.method == "POST":
            a = CustomUser.objects.get(pk=id)
            form = CustomUserProfileForm(request.POST, request.FILES,instance=a)
            if form.is_valid(): 
                form.save()
            return redirect("hosadminMyProfile")
        





#changeStatus Hospital
def changeStatusHospital(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
      if request.method == 'POST':
        getdata=json.load(request) 
        id = getdata['id']
        status = getdata['status']
        hospital = Hospital.objects.get(id=id)
        hospital.status = status
        hospital.save()      
        data = {
            'status': True,
               }
        return JsonResponse(data)
      else:
        data = {
            'status': False,
               }
        return JsonResponse(data)
    else:
        return redirect('/')

#changeStatusHospitalDoctor Hospital
def changeStatusHospitalDoctor(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
      if request.method == 'POST':
        getdata=json.load(request) 
        id = getdata['id']
        status = getdata['status']
        doctorlist = DoctorList.objects.get(id=id)
        doctorlist.is_active = status
        doctorlist.save()      
        data = {
            'status': True,
               }
        return JsonResponse(data)
      else:
        data = {
            'status': False,
               }
        return JsonResponse(data)
    else:
        return HttpResponse("Homepage")