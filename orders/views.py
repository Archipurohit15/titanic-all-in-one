from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import razorpay
from products.models import Product
from agents.models import Agent
from .models import Order, OrderItem

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def order_total(order):
    return sum(item.price_at_purchase * item.quantity for item in order.items.all())


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    if is_ajax(request):
        return JsonResponse({'quantity': cart[pid], 'cart_count': len(cart)})
    return redirect(request.META.get('HTTP_REFERER', '/'))


def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session['cart'] = cart
    if is_ajax(request):
        return JsonResponse({'quantity': cart[pid], 'cart_count': len(cart)})
    return redirect('view_cart')


def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    qty = 0
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]
        else:
            qty = cart[pid]
    request.session['cart'] = cart
    if is_ajax(request):
        return JsonResponse({'quantity': qty, 'cart_count': len(cart)})
    return redirect('view_cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
    request.session['cart'] = cart
    return redirect('view_cart')


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    item_count = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        item_count += quantity
        items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'orders/cart.html', {'items': items, 'total': total, 'item_count': item_count})


def checkout(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'Page is only for customers. Login / signup to view')
        return redirect('customer_login')
    customer=request.user.customer

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')

    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    # Order ships together, so overall estimate = the item that takes the longest.
    if items:
        order_min_days = max(item['product'].min_delivery_days for item in items)
        order_max_days = max(item['product'].max_delivery_days for item in items)
    else:
        order_min_days = order_max_days = None

    agents = Agent.objects.filter(is_approved=True)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        agent_id = request.POST.get('agent')

        agent = None
        if agent_id:
            agent = get_object_or_404(Agent, id=agent_id)

        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            pincode=pincode,
            referred_by=agent,
        )

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price,
            )

        request.session['cart'] = {}

        # TEMPORARY: real Razorpay keys nahi hain abhi, testing ke liye seedha "paid" mark kar do.
        # Jab real keys mil jaayein, .env mein RAZORPAY_BYPASS=False kar dena — ye poora block skip ho jaayega.
        if settings.RAZORPAY_BYPASS:
            order.status = 'paid'
            order.save()
            return redirect('order_success', order_id=order.id)
# ends here itna delete krdena baadme
 
        amount_paise = int(order_total(order) * 100)
        client = get_razorpay_client()
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
        })

        order.razorpay_order_id = razorpay_order['id']
        order.save()

        return render(request, 'orders/payment.html', {
            'order': order,
            'amount_paise': amount_paise,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        })

    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': total,
        'agents': agents,
        'customer': customer,
        'order_min_days': order_min_days,
        'order_max_days': order_max_days,
    })


def payment_verify(request):
    if request.method != 'POST':
        return redirect('view_cart')

    order_id = request.POST.get('order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    order = get_object_or_404(Order, id=order_id)
    client = get_razorpay_client()

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return redirect('payment_failed', order_id=order.id)

    order.status = 'paid'
    order.save()

    return redirect('order_success', order_id=order.id)


def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/payment_failed.html', {'order': order})


def retry_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, status='pending')

    amount_paise = int(order_total(order) * 100)
    client = get_razorpay_client()
    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1,
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return render(request, 'orders/payment.html', {
        'order': order,
        'amount_paise': amount_paise,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total = sum(item.price_at_purchase * item.quantity for item in order.items.all())
    return render(request, 'orders/order_success.html', {'order': order, 'total': total})

def verify_delivery(request):
    error = None
    success = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        otp = request.POST.get('otp')

        order = Order.objects.filter(id=order_id).first()

        if not order:
            error = 'Ye Order ID exist nahi karta.'
        elif order.status == 'delivered':
            error = 'Ye order pehle se delivered mark ho chuka hai.'
        elif order.status != 'shipped':
            error = 'Ye order abhi shipped nahi hua hai, OTP verify nahi ho sakta.'
        elif order.delivery_otp != otp:
            error = 'Galat OTP. Dobara try karo.'
        else:
            order.status = 'delivered'
            order.save()
            success = f'Order #{order.id} successfully delivered mark ho gaya!'

    return render(request, 'orders/verify_delivery.html', {'error': error, 'success': success})