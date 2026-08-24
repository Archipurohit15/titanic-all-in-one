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
    list_display = ('thumbnail', 'name', 'category', 'price', 'stock', 'commission_percent', 'min_delivery_days', 'max_delivery_days')
    list_filter = ('category',)
    search_fields = ('name',)
    list_editable = ('price', 'stock', 'commission_percent', 'min_delivery_days', 'max_delivery_days')

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.image.url)
        elif obj.auto_image_url:
            return format_html('<img src="{}" style="height:40px; border-radius:6px;">', obj.auto_image_url)
        return "—"
    thumbnail.short_description = "Image"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Categories.objects.filter(children__isnull=True).order_by(
                'parent__parent__name', 'parent__name', 'name'
            )
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == "category":
            field.label_from_instance = lambda obj: (
                f"{obj.parent.parent.name if obj.parent and obj.parent.parent else ''} › "
                f"{obj.parent.name if obj.parent else ''} › {obj.name}"
            )
        return field