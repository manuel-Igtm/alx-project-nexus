from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlockedIPViewSet, AllowedIPViewSet, IPAccessLogViewSet,
    SecurityAlertViewSet, SecurityDashboardView, my_ip
)

router = DefaultRouter()
router.register('blocked-ips', BlockedIPViewSet, basename='blocked-ip')
router.register('allowed-ips', AllowedIPViewSet, basename='allowed-ip')
router.register('access-logs', IPAccessLogViewSet, basename='access-log')
router.register('alerts', SecurityAlertViewSet, basename='security-alert')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', SecurityDashboardView.as_view(), name='security-dashboard'),
    path('my-ip/', my_ip, name='my-ip'),
]
