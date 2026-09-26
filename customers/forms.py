from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomerSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password