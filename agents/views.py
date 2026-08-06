from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
import random
import string
from .models import Agent, Commission
from .forms import AgentSignupForm
from orders.models import Order


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


def agent_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'agent'):
            login(request, user)
            return redirect('agent_dashboard')
        else:
            messages.error(request, 'Galat username ya password.')

    return render(request, 'agents/login.html')


def agent_logout(request):
    logout(request)
    return redirect('agent_login')


@login_required(login_url='agent_login')
def agent_dashboard(request):
    if not hasattr(request.user, 'agent'):
        messages.error(request, 'Ye page sirf agents ke liye hai.')
        return redirect('agent_login')

    agent = request.user.agent

    if not agent.is_approved:
        return render(request, 'agents/dashboard.html', {
            'agent': agent,
            'pending_approval': True,
        })

    orders = Order.objects.filter(referred_by=agent).order_by('-created_at')
    commissions = Commission.objects.filter(agent=agent).order_by('-created_at')

    total_earnings = commissions.aggregate(total=Sum('amount'))['total'] or 0
    pending_amount = commissions.filter(is_paid=False).aggregate(total=Sum('amount'))['total'] or 0
    paid_amount = commissions.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    payout_history = commissions.filter(is_paid=True).order_by('-paid_at')

    context = {
        'agent': agent,
        'pending_approval': False,
        'orders': orders,
        'total_orders': orders.count(),
        'total_earnings': total_earnings,
        'pending_amount': pending_amount,
        'paid_amount': paid_amount,
        'payout_history': payout_history,
    }
    return render(request, 'agents/dashboard.html', context)