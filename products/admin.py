from django.contrib import admin
from django.utils.html import format_html
from .models import Categories, Product


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'parent', 'commission_percent')
    list_filter = ('parent',)
    search_fields = ('name',)

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.image.url)
        return "—"
    thumbnail.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumbnail', 'name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('price', 'stock')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.image.url)
        elif obj.auto_image_url:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.auto_image_url)
        return "—"
    thumbnail.short_description = "Image"