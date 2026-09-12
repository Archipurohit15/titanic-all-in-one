from django import forms
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message='Valid 10-digit mobile number daalo (jaise 9876543210).'
)


class CustomerSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=10, validators=[phone_validator])
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, help_text="Kam se kam 6 characters")