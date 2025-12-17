"""
API URL Configuration for Project Nexus E-Commerce Backend.

This module defines all REST API endpoints with proper versioning.
"""
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views import (
    ProductViewSet, CategoryViewSet, OrderViewSet,
    CartViewSet, OrderItemViewSet, CartItemViewSet,
    PaymentViewSet, NotificationViewSet, health_check
)

# =============================================================================
# ROUTER CONFIGURATION
# =============================================================================

router = DefaultRouter()

# Core e-commerce endpoints
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('orders', OrderViewSet, basename='order')
router.register('order-items', OrderItemViewSet, basename='order-item')
router.register('carts', CartViewSet, basename='cart')
router.register('cart-items', CartItemViewSet, basename='cart-item')
router.register('payments', PaymentViewSet, basename='payment')
router.register('notifications', NotificationViewSet, basename='notification')

# =============================================================================
# URL PATTERNS
# =============================================================================

urlpatterns = [
    # Authentication
    path('auth/', include('users.urls')),
    
    # Health check
    path('health/', health_check, name='api-health-check'),
]

# Add router URLs
urlpatterns += router.urls
