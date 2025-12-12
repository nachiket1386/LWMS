from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User
from companies.models import Company


class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'company']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        if self.current_user and not self.current_user.is_root():
            self.fields['role'].choices = [
                (User.Role.ADMIN, 'Admin'),
                (User.Role.USER1, 'User1'),
            ]
            if self.current_user.company:
                self.fields['company'].initial = self.current_user.company
                self.fields['company'].disabled = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'company', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        if self.current_user and not self.current_user.is_root():
            self.fields['role'].choices = [
                (User.Role.ADMIN, 'Admin'),
                (User.Role.USER1, 'User1'),
            ]
            if self.instance.role == User.Role.ROOT:
                for field in self.fields:
                    self.fields[field].disabled = True


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No user found with this email address.')
        return email
