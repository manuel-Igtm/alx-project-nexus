from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


ORDER_STATUS = (
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("cancelled", "Cancelled"),
    ("refunded", "Refunded"),
)


class Cart(models.Model):
    # Either user or session_key defines cart ownership
    user = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "variant")


class Order(models.Model):
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,related_name='orders')#products.orders
    created_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name='orders')#users.orders
    created = models.DateTimeField(auto_now=True)
    update = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20,choices=ORDER_STATUS,default='Pending')
    shipping_address = models.JSONField(null=True, blank=True)  # simplified

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey("products.ProductVariant", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)