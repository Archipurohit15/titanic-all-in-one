from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Agent

phone_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message='Valid 10-digit mobile number daalo (jaise 9876543210).'
)


class AgentSignupForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, help_text="Kam se kam 6 characters")
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=10, validators=[phone_validator])