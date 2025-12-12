from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
    upload_type = forms.ChoiceField(choices=[
        ('attendance', 'Attendance'),
        ('employee', 'Employee'),
        ('manday', 'Manday'),
        ('overtime', 'Overtime'),
    ])
