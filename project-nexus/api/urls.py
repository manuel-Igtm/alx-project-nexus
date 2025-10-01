from rest_framework.routers import DefaultRouter
from api.views import (ProductViewSet,  CategoryViewSet,OrderViewSet,CartViewSet,OrderItemViewSet,CartItemViewSet,PaymentViewSet,NotificationViewSet)
from django.urls import path,include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import health_check

router = DefaultRouter()

router.register('products',ProductViewSet)
router.register('categories',CategoryViewSet)
router.register('orders',OrderViewSet)
router.register('carts', CartViewSet)
router.register('cart-items', CartItemViewSet)
router.register('order-items', OrderItemViewSet)
router.register("payments", PaymentViewSet,basename='payment')
router.register("notifications", NotificationViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('auth/', include('users.urls')),  # Direct auth URLs to users app
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('health/', health_check, name='health-check'),
] 

urlpatterns +=  router.urls
