from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Product
from agents.models import Agent
from .models import Order,OrderItem

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


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
        return redirect('order_success', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'items': items,
        'total': total,
        'agents': agents,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total = sum(item.price_at_purchase * item.quantity for item in order.items.all())
    return render(request, 'orders/order_success.html', {'order': order, 'total': total})