from django.db import models

# Create your models here.

class Agent(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    referral_code = models.CharField(max_length=20, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name