from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from products.models import Product


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