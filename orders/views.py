from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from django.conf import settings
from django.contrib import messages
from datetime import timedelta
from decimal import Decimal
import re
from urllib.parse import quote, urlencode
import segno
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from products.models import Product
from .models import Order, OrderItem
from .utils import calculate_distance_km


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def order_total(order):
    return sum(item.price_at_purchase * item.quantity for item in order.items.all())


def build_upi_link(order):
    params = {
        'pa': settings.UPI_ID,
        'pn': settings.UPI_PAYEE_NAME,
        'am': f"{order.grand_total:.2f}",
        'cu': 'INR',
        'tn': f"Order TIT{order.id}",
    }
    return 'upi://pay?' + urlencode(params, quote_via=quote)


def build_whatsapp_link(order, utr=''):
    text = (
        f"Hi, I have paid for Order #TIT{order.id}.\n"
        f"Amount: Rs {order.grand_total:.2f}\n"
        f"Name: {order.full_name}\n"
        f"UTR: {utr or '(screenshot attached)'}"
    )
    return f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(text)}"


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
                stale_ids.append(pid)

        products = Product.objects.in_bulk(valid_int_ids)

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
    customer = request.user.customer

    cart = request.session.get('cart', {})
    if not cart:
        return redirect('view_cart')

    items, total = get_valid_cart_items(request)
    if not items:
        messages.error(request, 'Aapka cart update ho gaya tha (kuch products ab available nahi hain). Dobara add karo.')
        return redirect('view_cart')

    if items:
        order_min_days = max(item['product'].min_delivery_days for item in items)
        order_max_days = max(item['product'].max_delivery_days for item in items)
    else:
        order_min_days = order_max_days = None

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
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
                'items': items, 'total': total, 'customer': customer,
                'store_lat': str(settings.STORE_LATITUDE),
                'store_lng': str(settings.STORE_LONGITUDE),
                'order_min_days': order_min_days, 'order_max_days': order_max_days,
            })

        distance_km = calculate_distance_km(lat, lng)

        # The agent is fixed at signup. Only an approved agent earns commission.
        agent = customer.referred_by
        if agent is not None and not agent.is_approved:
            agent = None

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

        return redirect('upi_payment', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': total,
        'customer': customer,
        'store_lat': str(settings.STORE_LATITUDE),
        'store_lng': str(settings.STORE_LONGITUDE),
        'order_min_days': order_min_days,
        'order_max_days': order_max_days,
    })


@login_required(login_url='customer_login')
def upi_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if order.status != 'pending':
        return redirect('order_success', order_id=order.id)

    error = None
    if request.method == 'POST':
        utr = request.POST.get('utr_number', '').strip()
        if not re.fullmatch(r'\d{12}', utr):
            error = 'UTR / Transaction ID 12 digits ka hota hai. Apne UPI app mein check karke dobara daalo.'
        else:
            order.utr_number = utr
            order.save(update_fields=['utr_number'])
            return redirect('order_success', order_id=order.id)

    upi_link = build_upi_link(order)
    qr_svg = segno.make(upi_link, error='m').svg_data_uri(scale=6, border=2)

    return render(request, 'orders/upi_payment.html', {
        'order': order,
        'amount': order.grand_total,
        'upi_id': settings.UPI_ID,
        'upi_link': upi_link,
        'qr_svg': qr_svg,
        'whatsapp_link': build_whatsapp_link(order, order.utr_number),
        'error': error,
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
        'whatsapp_link': build_whatsapp_link(order, order.utr_number),
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