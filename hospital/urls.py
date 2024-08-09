
from django.contrib import admin
from django.urls import path
from . import views
from .views import *

urlpatterns = [ 
    path('home-hospital', views.homeHospital, name='homeHospital'),
    path('changeStatusHospital', views.changeStatusHospital, name='changeStatusHospital'),
    path('hospitalview/changeStatusHospitalDoctor', views.changeStatusHospitalDoctor, name='changeStatusHospitalDoctor'),
    path('addHospital', views.addHospital, name='addHospital'),
    path('hospitalDelete/<int:id>', views.hospitalDelete, name='hospitalDelete'),
    path('hospitalview/<str:getname>', views.hospitalview, name='hospitalview'),
    path('hospitalview/', hospitalview, name='hospitalview'),
    
    path('hospital/<int:hospital_id>/assign_wards/', assign_wards, name='assign_wards'),
    path('hosadmin/profile', views.hosadminMyProfile, name='hosadminMyProfile'),
    #profile pic update
    path('uploadHosAdminPropic/<int:id>', views.uploadHosAdminPropic, name='uploadHosAdminPropic'),
    
    #add new doctor
    path('addDoctor/<int:id>', views.addDoctor, name='addDoctor'),
    path('delete_selected_beds/', views.delete_selected_beds, name='delete_selected_beds'),
    path('assign_ward_to_hospital/', views.assign_ward_to_hospital, name='assign_ward_to_hospital'),
    path('generate_user_report/', views.generate_user_report, name='generate_user_report'),
    path('add_beds_to_ward/', views.add_beds_to_ward, name='add-beds-to-ward'),
    
    path('add_bed_to_ward/<int:ward_id>/', views.add_bed_to_ward, name='add-bed-to-ward'),
    path('generate_pdf_view/<int:users_id>/', views.generate_pdf_view, name='generate_pdf_view'),
    path('generate_doctor_reportfffff/', views.generate_doctor_report, name='generate_doctor_report'),
    path('generate_doctor_pdf_view/<int:users_id>/', views.generate_doctor_pdf_view, name='generate_doctor_pdf_view'),
    path('hospital/<int:hospital_id>/delete_selected_wards/', views.delete_selected_wards, name='delete_selected_wards'),
    path('assign-wards/<int:hospital_id>/', assign_wards, name='assign_wards'),
    path('add-ward/', add_ward, name='add_ward'),
    path('wards/', views.ward_list, name='ward_list'),
    path('print-wards-report/', views.print_wards_report, name='print_wards_report'),
    path('ward-lists/', views.ward_list, name='ward_list'),
    path('update-ward/<int:pk>/', views.update_ward, name='update_ward'),
    path('delete-ward/<int:pk>/', views.delete_ward, name='delete_ward'),
    path('doctor-list/', views.doctor_list, name='doctor_list'),
    path('patient-list/', views.patient_list, name='patient_list'),
    path('booking/<int:booking_id>/vacate/', views.vacate_bed, name='vacate_bed'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('get_beds_for_ward/', views.get_beds_for_ward, name='get_beds_for_ward'),
    path('move-and-remove-wards/<int:hospital_id>/', views.move_and_remove_wards, name='move_and_remove_wards'),
    
    path('reserve_bed/', views.reserve_bed, name='reserve_bed'),
    path('approve_bed/<int:booking_id>/', views.approve_bed, name='approve_bed'),
    path('delete_reservation/<int:booking_id>/', views.delete_reservation, name='delete_reservation'),
    
    path('bed_bookings/', views.bed_bookings, name='bed_bookings'),
    
    path('create_booking/', views.create_booking, name='create_booking'),
    
    path('book-bed/', book_bed, name='book_bed'),
    path('ajax/load-wards/', ajax_load_wards, name='ajax_load_wards'),
    path('ajax/load-beds/', ajax_load_beds, name='ajax_load_beds'),
    path('ajax/load-patients/', ajax_load_patients, name='ajax_load_patients'),

]
 