from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


NOTIFICATION_TYPE = (
    ("order", "Order Update"),
    ("payment", "Payment Update"),
    ("shipping", "Shipping Update"),
    ("system", "System Alert"),
)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.type}"

