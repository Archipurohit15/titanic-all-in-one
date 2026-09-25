from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Categories


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Product.objects.all()

    def location(self, obj):
        return reverse('product_detail', args=[obj.id])

    def lastmod(self, obj):
        return obj.created_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Categories.objects.filter(parent=None)

    def location(self, obj):
        return reverse('category_detail', args=[obj.id])


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "daily"

    def items(self):
        return ['product_list']

    def location(self, item):
        return reverse(item)