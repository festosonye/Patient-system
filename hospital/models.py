from django.db import models
from userSystem.models import CustomUser
from doctor.models import Doctor
from patient.models import Patient
import os
from django.conf import settings

class HospitalAdmin(models.Model):
    userID = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_active = models.IntegerField(default=1)
    
    def __str__(self):
        return f'{self.userID}'

class Hospital(models.Model):
    hos_Choices = (
        ('Nairobi Headquarters Hospital', 'Nairobi Headquarters Hospital'),
        ('Medical College Hospital', 'Medical College Hospital'),
        ('Family Health Center', 'Family Health Center'),
    )
    dct_Choices = (
        ('Nairobi', 'Nairobi'),
        ('Kisumu', 'Kisumu'),
        ('Nakuru', 'Nakuru'),
        ('Eldoret', 'Eldoret'),
        ('Naivasha', 'Naivasha'),
        ('Kiambu', 'Kiambu'),
        ('Kikuyu', 'Kikuyu'),
        ('Embu', 'Embu'),
    )

    name = models.CharField(max_length=100, unique=True)
    hos_type = models.CharField(max_length=100, choices=hos_Choices)
    district = models.CharField(max_length=100, choices=dct_Choices)
    createdBy = models.ForeignKey(HospitalAdmin, on_delete=models.CASCADE)
    createdOn = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.name} {self.district}'

class Ward(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    hospital = models.ForeignKey(Hospital, related_name='wards', on_delete=models.CASCADE, null=True, blank=True)

    def get_occupied_beds(self):
        return self.bookings.filter(state='occupied').count()

    @property
    def beds_remaining(self):
        return self.capacity - self.get_occupied_beds()

    def __str__(self):
        return self.name

class Bed(models.Model):
    bed_number = models.CharField(max_length=4)  # Alphanumeric bed identifiers
    ward = models.ForeignKey(Ward, related_name='beds', on_delete=models.CASCADE)

    def __str__(self):
        return f"Bed {self.bed_number} in {self.ward.name}"

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'


class Booking(models.Model):
    STATE_CHOICES = (
        ('reserved', 'Reserved'),
        ('approved', 'Approved'),
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
    )
    ward = models.ForeignKey(Ward, related_name='bookings', on_delete=models.CASCADE)
    bed_number = models.CharField(max_length=50)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='vacant')
    patient = models.ForeignKey(Patient, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Booking #{self.pk} - Ward: {self.ward.name}, Bed: {self.bed_number}, State: {self.state}"


class Timing(models.Model):
    Time_Choices = (
        ('7:00 AM - 9:00 AM', '7:00 AM - 9:00 AM'),
        ('10:00 AM - 12:00 PM', '10:00 AM - 12:00 PM'),
        ('1:00 PM - 3:00 PM', '1:00 PM - 3:00 PM'),
        ('4:00 PM - 6:00 PM', '4:00 PM - 6:00 PM'),
        ('NULL', 'Not Available'),
    )
    timeslot = models.CharField(max_length=100, choices=Time_Choices)
    is_active = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.timeslot}'

class List(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timing, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('hospital', 'doctor', 'department', 'timeslot')

    def __str__(self):
        return f'{self.doctor} {self.hospital} {self.department} {self.timeslot}'

class BookingPatient(models.Model):
    state_Choices = (
        ('COMPLETED', 'COMPLETED'),
        ('PENDING', 'PENDING'),
        ('DELETED', 'DELETED'),           
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    state = models.CharField(max_length=20, choices=state_Choices, null=True, blank=True)
    lists = models.ForeignKey(List, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    appointmentDate = models.DateField()
    documents = models.FileField(upload_to='hospital/prescription', null=True)

    def delete(self, *args, **kwargs):
        if self.documents:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.documents.name))  # Use settings.MEDIA_ROOT
        super(BookingPatient, self).delete(*args, **kwargs)

    def __str__(self):
        return f'Booking for {self.patient}'
