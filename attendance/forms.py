from django import forms
from django_filters import FilterSet, DateFromToRangeFilter, CharFilter, ChoiceFilter
from django.utils import timezone
from .models import Attendance, ManDays, Overtime, UploadBatch
from accounts.models import User


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'attendance_date', 'status', 'cost_center', 'hours_worked', 'supervisor_remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'attendance_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'cost_center': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Cost Center'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.5', 'min': '0', 'max': '24'}),
            'supervisor_remarks': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


class AttendanceFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    employee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    status = forms.ChoiceField(
        choices=[('', '-- All Statuses --')] + list(Attendance.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    cost_center = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Filter by cost center'})
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['employee'].queryset = company.users.filter(role__in=['ADMIN', 'USER1'])


class ManDaysForm(forms.ModelForm):
    class Meta:
        model = ManDays
        fields = ['employee', 'project', 'mandays_date', 'days_allocated', 'days_utilized', 'supervisor_remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'project': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Project Name'}),
            'mandays_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'days_allocated': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.25', 'min': '0'}),
            'days_utilized': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.25', 'min': '0'}),
            'supervisor_remarks': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


class ManDaysFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    employee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    project = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Filter by project'})
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['employee'].queryset = company.users.filter(role__in=['ADMIN', 'USER1'])


class OvertimeForm(forms.ModelForm):
    class Meta:
        model = Overtime
        fields = ['employee', 'overtime_date', 'hours', 'reason', 'supervisor_remarks']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'overtime_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'step': '0.5', 'min': '0', 'max': '24'}),
            'reason': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
            'supervisor_remarks': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


class OvertimeFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    employee = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    approved = forms.NullBooleanField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}, choices=[
            ('', '-- All --'),
            ('True', 'Approved'),
            ('False', 'Pending'),
        ])
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            self.fields['employee'].queryset = company.users.filter(role__in=['ADMIN', 'USER1'])
