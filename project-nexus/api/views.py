from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from django.contrib.auth import get_user_model
from .serializers import UserSerializer,ProductSerializer,CategorySerializer,OrderSerializer,OrderItemSerializer,CartItemSerializer,OrderItem,CartItem,CartSerializer,PaymentSerializer,NotificationSerializer
from products.models import Product,Category
from orders.models import   Order,Cart
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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


class PaymentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        # Basic payment intent creation
        order_id = request.data.get('order_id')
        # Integrate with payment provider
        return Response({"client_secret": "test_secret"})

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer