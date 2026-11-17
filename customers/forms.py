from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from agents.models import Agent


class CustomerSignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    agent = forms.ModelChoiceField(queryset=Agent.objects.none(), required=False)
    referral_code = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['agent'].queryset = Agent.objects.filter(is_approved=True)

    def clean(self):
        cleaned = super().clean()
        agent = cleaned.get('agent')
        code = (cleaned.get('referral_code') or '').strip()

        code_agent = None
        if code:
            code_agent = Agent.objects.filter(referral_code__iexact=code, is_approved=True).first()
            if code_agent is None:
                self.add_error('referral_code', 'Ye referral code galat hai ya agent approved nahi hai.')

        if agent and code_agent and agent != code_agent:
            self.add_error('referral_code', 'Dropdown aur referral code alag agents ke hain. Sirf ek hi chuno.')

        chosen = code_agent or agent

        # An agent cannot refer their own phone number (basic self-referral guard).
        phone = ''.join(ch for ch in (cleaned.get('phone') or '') if ch.isdigit())
        if chosen and phone and phone[-10:] == ''.join(ch for ch in chosen.phone if ch.isdigit())[-10:]:
            self.add_error('referral_code', 'Aap khud ko refer nahi kar sakte.')

        cleaned['referring_agent'] = chosen
        return cleaned

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password