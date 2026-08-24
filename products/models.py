from django.db import models
from .utils import fetch_image_for
# Create your models here.


# category class- konsi konsi categories hai - electronics - groceries - ye vo uski info sgtore karega 
class Categories(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='children', on_delete=models.CASCADE
    )
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    auto_image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image and not self.auto_image_url:
            self.auto_image_url = fetch_image_for(self.name)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"



# products class - saari product details store karega 
class Product(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    auto_image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.image and not self.auto_image_url:
            self.auto_image_url = fetch_image_for(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name