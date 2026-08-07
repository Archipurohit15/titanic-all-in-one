from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Customer
from .forms import CustomerSignupForm


def customer_signup(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            if User.objects.filter(username=email).exists():
                messages.error(request, 'Is email se pehle se account bana hua hai.')
                return render(request, 'customers/signup.html', {'form': form})

            user = User.objects.create_user(
                username=email,
                email=email,
                password=form.cleaned_data['password']
            )

            Customer.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
            )

            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = CustomerSignupForm()

    return render(request, 'customers/signup.html', {'form': form})


def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        # sirf customer hi is login se andar aa sakte hain, agent nahi
        if user is not None and hasattr(user, 'customer'):
            login(request, user)
            next_url = request.POST.get('next') or 'customer_dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Galat email ya password.')

    next_url = request.GET.get('next', '')
    return render(request, 'customers/login.html', {'next': next_url})


def customer_logout(request):
    logout(request)
    return redirect('customer_login')


@login_required(login_url='customer_login')
def customer_dashboard(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'Ye page sirf customers ke liye hai.')
        return redirect('customer_login')

    customer = request.user.customer
    orders = request.user.orders.all().order_by('-created_at')

    orders_with_total = []
    for order in orders:
        total = sum(item.price_at_purchase * item.quantity for item in order.items.all())
        orders_with_total.append({'order': order, 'total': total})

    return render(request, 'customers/dashboard.html', {
        'customer': customer,
        'orders_with_total': orders_with_total,
    })