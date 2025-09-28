from rest_framework.routers import DefaultRouter
from .views import (UserViewSet,ProductViewSet,  CategoryViewSet,OrderViewSet,CartViewSet,OrderItemViewSet,CartItemViewSet,PaymentViewSet,NotificationViewSet,CustomTokenObtainPairView, CustomTokenRefreshView
)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import health_check

router = DefaultRouter()

router.register('users',UserViewSet)
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
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('health/', health_check, name='health-check'),
] 

urlpatterns +=  router.urls
