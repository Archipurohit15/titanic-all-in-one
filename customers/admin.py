from django.contrib import admin
from .models import Customer

# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'referred_by', 'created_at')
    list_filter = ('referred_by',)
    search_fields = ('name', 'phone')