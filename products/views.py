from django.shortcuts import render, get_object_or_404
from .models import Product, Categories

def product_list(request):
    top_categories = Categories.objects.filter(parent=None)
    sections = []
    for cat in top_categories:
        groups = cat.children.all()
        if groups.exists():
            sections.append({'department': cat, 'groups': groups})

    return render(request, 'products/product_list.html', {'sections': sections})


def category_detail(request, category_id):
    department = get_object_or_404(Categories, id=category_id, parent=None)
    groups = department.children.all()
    cart = request.session.get('cart', {})

    group_sections = []
    for group in groups:
        products = list(Product.objects.filter(category__parent=group))
        for p in products:
            p.cart_qty = cart.get(str(p.id), 0)
        group_sections.append({'group': group, 'products': products})

    return render(request, 'products/category_detail.html', {
        'department': department,
        'group_sections': group_sections,
    })