from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from .models import Order


@receiver(post_save, sender=Order)
def generate_delivery_otp(sender, instance, **kwargs):
    order = instance

    # OTP sirf tab banega jab order "shipped" ho aur pehle se OTP na bana ho
    if order.status != 'shipped':
        return
    if order.delivery_otp:
        return

    otp = str(random.randint(100000, 999999))
    order.delivery_otp = otp
    order.save()