from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer,CategorySerializer,OrderSerializer,OrderItemSerializer,CartItemSerializer,OrderItem,CartItem,CartSerializer,PaymentSerializer,NotificationSerializer
from products.models import Product,Category
from orders.models import   Order,Cart
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from payments.models import Payment
from notifications.models import Notification
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .schema import *

class ProductViewSet(ModelViewSet):
    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of all products with optional filtering",
        manual_parameters=[
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('featured', openapi.IN_QUERY, description="Filter featured products", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price filter", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price filter", type=openapi.TYPE_NUMBER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in product names and descriptions", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response('List of products', product_response_schema),
            400: openapi.Response('Bad request', error_response_schema),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve specific product details",
        responses={
            200: openapi.Response('Product details', product_response_schema),
            404: openapi.Response('Product not found', error_response_schema),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new product (Admin only)",
        request_body=product_create_schema,
        responses={
            201: openapi.Response('Product created', product_response_schema),
            400: openapi.Response('Validation error', error_response_schema),
            401: openapi.Response('Authentication required', error_response_schema),
            403: openapi.Response('Admin permission required', error_response_schema),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_description="Create a new order",
        request_body=order_create_schema,
        responses={
            201: openapi.Response('Order created successfully'),
            400: openapi.Response('Invalid order data'),
            401: openapi.Response('Authentication required'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


# -- CART --
class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


# -- ORDER ITEM --
class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer


class PaymentViewSet(viewsets.ViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        # Basic payment intent creation
        order_id = request.data.get('order_id')
        # Integrate with payment provider
        return Response({"client_secret": "test_secret"})

class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer 

# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connections
from django.db.utils import OperationalError
from django.core.cache import cache
import datetime
import redis

@api_view(['GET'])
def health_check(request):
    """
    Comprehensive health check endpoint
    """
    # Database check
    try:
        db_conn = connections['default']
        db_conn.cursor()
        db_status = "connected"
    except OperationalError:
        db_status = "disconnected"

    # Cache check
    try:
        cache.set('health_check', 'test', 1)
        cache_status = "connected"
    except redis.ConnectionError:
        cache_status = "disconnected"

    return Response({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "services": {
            "database": db_status,
            "cache": cache_status,
        },
        "version": "1.0.0"
    })