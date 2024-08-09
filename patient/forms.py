from django import forms

class ReportForm(forms.Form):
    pass  # This is an empty form as we don't need user input for generating reports

class AppointmentReportForm(forms.Form):
    pass  # Empty form for appointment report

class BookingReportForm(forms.Form):
    pass  # Empty form for booking report