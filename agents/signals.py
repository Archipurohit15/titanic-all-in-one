from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .models import Commission


@receiver(post_save, sender=Order)
def create_commission_on_paid(sender, instance, **kwargs):
    order = instance

    # commission sirf tab banega jab: order paid ho, agent assign ho, aur pehle se commission na bana ho
    if order.status != 'paid':
        return
    if not order.referred_by:
        return
    if hasattr(order, 'commission'):
        return

    total_commission = 0
    for item in order.items.all():
        category = item.product.category
        item_total = item.price_at_purchase * item.quantity
        total_commission += item_total * (category.commission_percent / 100)

    Commission.objects.create(
        order=order,
        agent=order.referred_by,
        amount=total_commission,
    )