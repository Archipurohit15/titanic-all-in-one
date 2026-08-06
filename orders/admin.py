from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'referred_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('full_name', 'phone')
    inlines = [OrderItemInline]