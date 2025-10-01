from rest_framework import serializers
from django.contrib.auth import get_user_model
from products.models import Product,Category
from orders.models import Order,Cart, CartItem,OrderItem
from products.models import Product, ProductVariant
from products.serializers import ProductVariantSerializer
from payments.models import Payment

from notifications.models import Notification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'  


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'   


# -- CART --
class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source="variant",
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "variant", "variant_id", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "session_key", "created_at", "updated_at", "items"]


# -- ORDER --
class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source="variant",
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "variant", "variant_id", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)  # shows username by default
    product = ProductSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "total", "product", "created_by",
            "created", "update", "status",
            "shipping_address", "items"
        ]

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

