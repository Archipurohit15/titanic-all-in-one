from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from datetime import timedelta
import razorpay
from products.models import Product
from agents.models import Agent
from .models import Order, OrderItem
from .utils import calculate_distance_km
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit



def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def order_total(order):
    return sum(item.price_at_purchase * item.quantity for item in order.items.all())


def get_valid_cart_items(request):
    """
    Session cart ko DB se resolve karta hai, aur agar koi product_id
    ab database mein exist nahi karta (delete ho gaya / stale session),
    use crash karne ke bajaye chupchaap cart se hata deta hai.
    Returns: (items list, total)
    """
    cart = request.session.get('cart', {})
    items = []
    total = 0
    stale_ids = []

    if cart:
        valid_int_ids = []
        for pid in cart.keys():
            try:
                valid_int_ids.append(int(pid))
            except (TypeError, ValueError):
                stale_ids.append(pid)  # corrupted entry, drop it too

        products = Product.objects.in_bulk(valid_int_ids)  # {id: Product}

        for product_id, quantity in cart.items():
            if product_id in stale_ids:
                continue
            product = products.get(int(product_id))
            if product is None:
                stale_ids.append(product_id)
                continue
            subtotal = product.price * quantity
            total += subtotal
            items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    if stale_ids:
        for sid in stale_ids:
            cart.pop(sid, None)
        request.session['cart'] = cart
        request.session.modified = True

    return items, total


def add_to_cart(request, product_id):
    if not Product.objects.filter(id=product_id).exists():
        if is_ajax(request):
            return JsonResponse({'error': 'Product not found'}, status=404)
        messages.error(request, 'Ye product ab available nahi hai.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

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
    items, total = get_valid_cart_items(request)
    item_count = sum(item['quantity'] for item in items)
    return render(request, 'orders/cart.html', {'items': items, 'total': total, 'item_count': item_count})


def checkout(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'Page is only for customers. Login / signup to view')
        return redirect('customer_login')
    customer=request.user.customer

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')

    items, total = get_valid_cart_items(request)
    if not items:
        messages.error(request, 'Aapka cart update ho gaya tha (kuch products ab available nahi hain). Dobara add karo.')
        return redirect('view_cart')

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
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')

        errors = []
        if not full_name:
            errors.append('Naam daalo.')
        if not phone:
            errors.append('Phone number daalo.')
        if not address:
            errors.append('Address daalo.')
        if not pincode:
            errors.append('Pincode daalo.')
        if not lat or not lng:
            errors.append('Delivery location detect karo checkout complete karne ke liye.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'orders/checkout.html', {
                'items': items, 'total': total, 'agents': agents, 'customer': customer,
                'store_lat': str(settings.STORE_LATITUDE),
                'store_lng': str(settings.STORE_LONGITUDE),
                'order_min_days': order_min_days, 'order_max_days': order_max_days,
            })

        distance_km = calculate_distance_km(lat, lng)

        agent = None
        if agent_id:
            agent = get_object_or_404(Agent, id=agent_id)

        convenience_charge = 0
        if distance_km is not None and distance_km > 5:
            convenience_charge = (total * Decimal('0.02')).quantize(Decimal('0.01'))


        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            pincode=pincode,
            referred_by=agent,
            delivery_distance_km=distance_km,
            convenience_charge=convenience_charge,
        )

        for entry in items:
            OrderItem.objects.create(
                order=order,
                product=entry['product'],
                quantity=entry['quantity'],
                price_at_purchase=entry['product'].price,
            )

        request.session['cart'] = {}

        # TEMPORARY: real Razorpay keys nahi hain abhi, testing ke liye seedha "paid" mark kar do.
        # Jab real keys mil jaayein, .env mein RAZORPAY_BYPASS=False kar dena — ye poora block skip ho jaayega.
        if settings.RAZORPAY_BYPASS:
            order.status = 'paid'
            order.save()
            return redirect('order_success', order_id=order.id)
# ends here itna delete krdena baadme
 
        amount_paise = int(order.grand_total * 100)
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
        'store_lat': str(settings.STORE_LATITUDE),
        'store_lng': str(settings.STORE_LONGITUDE),
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

    order = get_object_or_404(Order, id=order_id, customer=request.user)
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


@login_required(login_url='customer_login')
def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/payment_failed.html', {'order': order})


@login_required(login_url='customer_login')
def retry_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user, status='pending')

    amount_paise = int(order.grand_total * 100)
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



@login_required(login_url='customer_login')
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    total = sum(item.price_at_purchase * item.quantity for item in order.items.all())
    grand_total = total + order.convenience_charge

    items = list(order.items.all())
    estimated_delivery_start = None
    estimated_delivery_end = None
    if items:
        order_min_days = max(item.product.min_delivery_days for item in items)
        order_max_days = max(item.product.max_delivery_days for item in items)
        estimated_delivery_start = order.created_at + timedelta(days=order_min_days)
        estimated_delivery_end = order.created_at + timedelta(days=order_max_days)
    else:
        order_min_days = order_max_days = None

    return render(request, 'orders/order_success.html', {
        'order': order,
        'total': total,
        'grand_total': grand_total,
        'order_min_days': order_min_days,
        'order_max_days': order_max_days,
        'estimated_delivery_start': estimated_delivery_start,
        'estimated_delivery_end': estimated_delivery_end,
    })



@ratelimit(key='ip', rate='5/10m', block=True)
def verify_delivery(request):
    error = None
    success = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        otp = request.POST.get('otp')
        staff_pin = request.POST.get('staff_pin')

        if staff_pin != settings.STAFF_DELIVERY_PIN:
            error = 'Galat staff PIN.'
        else:
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