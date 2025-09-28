from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify


User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class Product(models.Model):
    name = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(max_length=100)
    price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    category = models.ForeignKey(Category,on_delete=models.CASCADE, related_name='products') #category.products
    created_by = models.ForeignKey(User,on_delete=models.CASCADE, related_name='products',default=None , null=True) #users.products
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64, unique=True)
    attributes = models.JSONField(default=dict, blank=True)  # e.g. {"size":"M","color":"red"}
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} — {self.sku}"