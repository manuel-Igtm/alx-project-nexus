from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import UserSerializer,ProductSerializer,CategorySerializer,OrderSerializer,OrderItemSerializer,CartItemSerializer,OrderItem,CartItem,CartSerializer,PaymentSerializer,SearchQuerySerializer,ShippingSerializer,DiscountSerializer,NotificationSerializer
from products.models import Product,Category
from orders.models import   Order,Cart
from rest_framework.permissions import IsAuthenticated

from payments.models import Payment
from notifications.models import Notification

User = get_user_model()

class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(ModelViewSet):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

class CategoryViewSet(ModelViewSet):
    queryset =  Category.objects.all()
    serializer_class = CategorySerializer

class OrderViewSet(ModelViewSet):
    queryset =  Order.objects.all()
    serializer_class = OrderSerializer


# ---------------- CART ----------------
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


# ---------------- ORDER ITEM ----------------
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer