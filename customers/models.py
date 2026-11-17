from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    # Set once at signup. All of this customer's orders earn commission for this agent.
    referred_by = models.ForeignKey(
        'agents.Agent',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='referred_customers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name