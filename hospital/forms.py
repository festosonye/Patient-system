from django import forms
from .models import *


class BookingForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), empty_label="Select Hospital", required=True)
    ward = forms.ModelChoiceField(queryset=Ward.objects.none(), empty_label="Select Ward", required=True)
    bed = forms.ModelChoiceField(queryset=Bed.objects.none(), empty_label="Select Bed", required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.none(), empty_label="Select Patient", required=True)
    state = forms.ChoiceField(choices=[('booked', 'Booked'), ('available', 'Available')], required=True)

    class Meta:
        model = Booking
        fields = ['hospital', 'ward', 'bed', 'patient', 'state']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'hospital' in self.data:
            try:
                hospital_id = int(self.data.get('hospital'))
                self.fields['ward'].queryset = Ward.objects.filter(hospital_id=hospital_id).order_by('name')
            except (ValueError, TypeError):
                pass

        if 'ward' in self.data:
            try:
                ward_id = int(self.data.get('ward'))
                self.fields['bed'].queryset = Bed.objects.filter(ward_id=ward_id).order_by('id')
                self.fields['patient'].queryset = Patient.objects.filter(bookings__ward_id=ward_id).distinct().order_by('userID__username')
            except (ValueError, TypeError):
                pass
        else:
            self.fields['ward'].queryset = Ward.objects.none()
            self.fields['bed'].queryset = Bed.objects.none()
            self.fields['patient'].queryset = Patient.objects.none()
         

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name', 'capacity', 'hospital']

    def clean_name(self):
        name = self.cleaned_data['name']
        if Ward.objects.exclude(pk=self.instance.pk).filter(name=name).exists():
            raise forms.ValidationError("A ward with this name already exists.")
        return name

    def save(self, commit=True):
        ward = super().save(commit=False)
        if commit:
            ward.save()
        return ward


class BedForm(forms.Form):
    ward_id = forms.ModelChoiceField(queryset=Ward.objects.all(), empty_label=None, widget=forms.Select(attrs={'class': 'form-control'}))
    bed_number = forms.CharField(help_text="Enter bed number (e.g., 1, 1a)", required=True)

    def clean_bed_number(self):
        bed_number = self.cleaned_data['bed_number'].strip()
        # Handle alphanumeric identifiers or other validation here if needed
        return bed_number


class ReserveBedForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ward', 'bed_number', 'patient']

class ApproveBedForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ward', 'bed_number', 'patient']


class BookingPatientForm(forms.ModelForm):

    class Meta:
        model = BookingPatient
        fields = ('documents',)
        labels = {'documents': ('Upload Prescription')}

class AddBedsForm(forms.Form):
    ward = forms.ModelChoiceField(queryset=Ward.objects.all(), label="Select Ward")
    bed_numbers = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter comma-separated bed numbers'}), label="Bed Numbers")
    
    def clean_bed_number(self):
        bed_number = self.cleaned_data['bed_number'].strip()
        # Handle alphanumeric identifiers or other validation here if needed
        return bed_number
    
class AddHospitalForm(forms.ModelForm):

    class Meta:
        model = Hospital
        fields = ('name', 'hos_type', 'district')
        labels = {
            'name': ('Hospital Name'),
            'hos_type': ('Type of Hospital'),
            'district': ('District'),
        }


class AddDoctorForm(forms.ModelForm):

    class Meta:
        model = List
        exclude = ['hospital']


class AssignWardsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        hospital = kwargs.pop('hospital', None)  # Ensure hospital is popped from kwargs safely
        super().__init__(*args, **kwargs)
        
        # Customize form initialization based on hospital if needed
        if hospital:
            self.fields['wards'] = forms.ModelMultipleChoiceField(
                queryset=Ward.objects.filter(hospital__isnull=True),
                widget=forms.CheckboxSelectMultiple,
                required=True,
            )