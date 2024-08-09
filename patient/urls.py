
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [ 
    path('patient-home', views.homePatient, name='homePatient'),
    path('patient/newbooking', views.patientNewbooking, name='patientNewbooking'),
    path('patient/newbooking/choose-doctor', views.patientChooseDoctor, name='patientChooseDoctor'),
    path('patient/getHospitalDepartment', views.getHospitalDepartment, name='getHospitalDepartment'),
    path('patientSaveBooking/<str:dep>/<str:hosname>/<str:uhid>', views.patientSaveBooking, name='patientSaveBooking'),
    path('patient-home/profile/mybooking', views.patientViewBooking, name='patientViewBooking'),
    path('patient/profile', views.patientMyProfile, name='patientMyProfile'),
        #url for mark deleted
    path('patient/myappointments/change/markDeleted/<int:id>', views.patientMarkDeleted, name='patientMarkDeleted'),

    path('uploadPatientPropic/<int:id>', views.uploadPatientPropic, name='uploadPatientPropic'),
    
   
   path('generate_appointment_report/', views.generate_appointment_report, name='generate_appointment_report'),
    
    path('generate_pdf/<int:booking_id>/', views.generate_pdf_view, name='generate_pdf'),
    # Other URLs...
]
