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
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price (MRP) — chhodo khaali agar discount nahi dena")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price — jo customer actually pay karega")
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    auto_image_url = models.URLField(blank=True, null=True)
    min_delivery_days = models.PositiveIntegerField(default=3, help_text="Minimum days for delivery (e.g. 3)")
    max_delivery_days = models.PositiveIntegerField(default=7, help_text="Maximum days for delivery (e.g. 7)")
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Agent commission % earned on this product")
    variant_of = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='variants',
        help_text="Agar ye kisi product ka variant (color/size/wattage/capacity) hai, us 'main' product ko yahan select karo"
    )
    variant_type = models.CharField(
        max_length=30, blank=True,
        help_text="Variant ka naam — jaise: Wattage, Capacity, Colour, Size (sabhi variants mein same rakhna)"
    )
    variant_label = models.CharField(
        max_length=50, blank=True,
        help_text="Is specific product ka variant value — jaise: '10 Watt', '15L', 'Cocoa Brown'"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

    @property
    def has_discount(self):
        return self.mrp and self.mrp > self.price

    @property
    def discount_percent(self):
        if self.has_discount:
            return round(((self.mrp - self.price) / self.mrp) * 100)
        return 0

    @property
    def discount_amount(self):
        if self.has_discount:
            return self.mrp - self.price
        return 0

    @property
    def delivery_estimate_text(self):
        if self.min_delivery_days == self.max_delivery_days:
            return f"{self.min_delivery_days} day{'s' if self.min_delivery_days != 1 else ''}"
        return f"{self.min_delivery_days}-{self.max_delivery_days} days"

    @property
    def variant_family(self):
        """
        Isi product ke saare variants return karta hai (khud ko bhi milaake) —
        chahe wo color ho, wattage ho, ya capacity (litre) — kuch bhi.
        """
        main_product = self.variant_of or self
        family = [main_product] + list(main_product.variants.all())
        return family

    def save(self, *args, **kwargs):
        if not self.image and not self.auto_image_url:
            self.auto_image_url = fetch_image_for(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name