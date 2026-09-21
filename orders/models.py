from django.db import models
from products.models import Product
from agents.models import Agent
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]
    customer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    referred_by = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_otp = models.CharField(max_length=6, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    convenience_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} — {self.status}"

    @property
    def items_total(self):
      return sum(item.price_at_purchase * item.quantity for item in self.items.all())

    @property
    def grand_total(self):
      return self.items_total + self.convenience_charge


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.display_name}"