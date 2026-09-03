from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Categories

def product_list(request):
    top_categories = Categories.objects.filter(parent=None)
    sections = []
    for cat in top_categories:
        groups = cat.children.all()
        if groups.exists():
            sections.append({'department': cat, 'groups': groups})

    return render(request, 'products/product_list.html', {'sections': sections})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product.cart_qty = cart.get(str(product.id), 0)

     # Breadcrumb trail — chahe category kitni bhi deep/flat ho, safe tareeke se build karo
    trail = []
    node = product.category
    while node:
        trail.append(node)
        node = node.parent
    trail.reverse()  # ab trail[0] = department (sabse upar), aakhri = product ki khud ki category

    department = trail[0]

    related_products = Product.objects.filter(category=product.category, variant_of__isnull=True).exclude(id=product.id).exclude(id=product.variant_of_id)[:4]

    return render(request, 'products/product_detail.html', {
        'product': product,
        'department': department,
        'breadcrumb_trail': trail,
        'related_products': related_products,
    })


def get_leaf_categories(department):
    """Department ke andar jitni bhi deep-nested categories hain, sirf leaf-level (jinka koi child nahi) wapas karo."""
    leaves = []

    def collect(category):
        children = category.children.all()
        if children.exists():
            for child in children:
                collect(child)
        else:
            leaves.append(category)

    for top_child in department.children.all():
        collect(top_child)

    return leaves


def category_detail(request, category_id):
    department = get_object_or_404(Categories, id=category_id, parent=None)
    cart = request.session.get('cart', {})

    leaf_categories = get_leaf_categories(department)

    group_sections = []
    for leaf in leaf_categories:
        products = list(Product.objects.filter(category=leaf, variant_of__isnull=True))
        for p in products:
            p.cart_qty = cart.get(str(p.id), 0)
        group_sections.append({'group': leaf, 'products': products})

    return render(request, 'products/category_detail.html', {
        'department': department,
        'group_sections': group_sections,
    })


def search_results(request):
    query = request.GET.get('q', '').strip()
    cart = request.session.get('cart', {})
    products = []

    if query:
        products = list(
            Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query),
                variant_of__isnull=True
            ).distinct()
        )
        for p in products:
            p.cart_qty = cart.get(str(p.id), 0)

    return render(request, 'products/search_results.html', {
        'query': query,
        'products': products,
    })