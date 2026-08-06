from django.contrib import admin
from .models import Agent,Commission
# Register your models here.

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'referral_code', 'is_approved', 'created_at')
    list_filter = ('is_approved',)

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'agent', 'amount', 'is_paid', 'created_at', 'paid_at')
    list_filter = ('is_paid',)

