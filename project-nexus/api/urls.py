from rest_framework.routers import DefaultRouter
from .views import UserViewSet,ProductViewSet,CategoryViewSet,OrderViewSet,CartViewSet,OrderItemViewSet,CartItemViewSet,PaymentViewSet,SearchQueryViewSet,ShippingViewSet,DiscountViewSet,NotificationViewSet
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.urls import path

router = DefaultRouter()

router.register('users',UserViewSet)
router.register('products',ProductViewSet)
router.register('categories',CategoryViewSet)
router.register('orders',OrderViewSet)
router.register('carts', CartViewSet)
router.register('cart-items', CartItemViewSet)
router.register('order-items', OrderItemViewSet)
router.register("payments", PaymentViewSet)
router.register("search", SearchQueryViewSet)
router.register("shipping", ShippingViewSet)
router.register("discounts", DiscountViewSet)
router.register("notifications", NotificationViewSet)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 

urlpatterns +=  router.urls
