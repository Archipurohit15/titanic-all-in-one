from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_display',)
    fields = ('product_display', 'product', 'quantity', 'price_at_purchase')

    def product_display(self, obj):
        return obj.product.display_name
    product_display.short_description = "Product (with variant)"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'grand_total_display', 'utr_number', 'referred_by', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'full_name', 'phone', 'utr_number')
    inlines = [OrderItemInline]
    actions = ['mark_as_paid']

    def grand_total_display(self, obj):
        return f"Rs {obj.grand_total}"
    grand_total_display.short_description = "Total"

    @admin.action(description="Mark selected orders as PAID (after checking UPI/bank)")
    def mark_as_paid(self, request, queryset):
        # .save() per order (not .update()) so the commission signal fires.
        count = 0
        for order in queryset.filter(status='pending'):
            order.status = 'paid'
            order.save()
            count += 1
        self.message_user(request, f"{count} order(s) marked as paid.")
