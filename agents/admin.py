from django.contrib import admin
from .models import Agent
# Register your models here.

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'referral_code', 'is_approved', 'created_at')
    list_filter = ('is_approved',)