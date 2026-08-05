from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
import random
import string
from .models import Agent
from .forms import AgentSignupForm


def generate_referral_code():
    return 'AG' + ''.join(random.choices(string.digits, k=6))


def agent_signup(request):
    if request.method == 'POST':
        form = AgentSignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Ye username already liya jaa chuka hai.')
                return render(request, 'agents/signup.html', {'form': form})

            user = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password']
            )

            Agent.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                referral_code=generate_referral_code(),
            )

            login(request, user)
            return redirect('agent_dashboard')
    else:
        form = AgentSignupForm()

    return render(request, 'agents/signup.html', {'form': form})