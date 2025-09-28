from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


PAYMENT_METHODS = (
    ("chapa", "Chapa"),
    ("mpesa", "M-Pesa"),
    ("cash", "Cash on Delivery"),
)

PAYMENT_STATUS = (
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("refunded", "Refunded"),
)


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    chapa_tx_ref = models.CharField(max_length=255, blank=True, null=True)  # from Chapa API
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    provider = models.CharField(max_length=100, blank=True, null=True)   # e.g. Chapa
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.method} - {self.status}"
