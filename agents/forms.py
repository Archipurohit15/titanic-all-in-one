from django import forms
from django.contrib.auth.models import User
from .models import Agent


class AgentSignupForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)