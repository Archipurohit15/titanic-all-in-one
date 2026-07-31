from django.shortcuts import render,get_object_or_404
from .models import Product,Categories
# Create your views here.


def product_list(request):
    top_categories = Categories.objects.filter(parent=None)
    sections = []
    for cat in top_categories:
        products = Product.objects.filter(category__parent=cat)[:4]
        if products.exists():
            sections.append({'category': cat, 'products': products})
    return render(request, 'products/product_list.html', {'sections': sections})


def base(request):
    return render(request,'base.html')


def category_detail(request, category_id):
    category = get_object_or_404(Categories, id=category_id, parent=None)
    subcategories = category.children.all()
    products = Product.objects.filter(category__parent=category)
    return render(request, 'products/category_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'products': products,
    })