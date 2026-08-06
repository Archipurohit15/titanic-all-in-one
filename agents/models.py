from django.db import models
from django.contrib.auth.models import User


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    referral_code = models.CharField(max_length=20, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Commission(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='commission')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='commissions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Commission #{self.id} - {self.agent.name} - ₹{self.amount}"    