from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.cache import cache
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import BlockedIP, AllowedIP, IPAccessLog, LoginAttempt, SecurityAlert
from .serializers import (
    BlockedIPSerializer, AllowedIPSerializer, IPAccessLogSerializer,
    LoginAttemptSerializer, SecurityAlertSerializer, SecurityDashboardSerializer,
    BlockIPRequestSerializer
)
from .middleware import get_client_ip


class IsAdminUser(permissions.BasePermission):
    """Custom permission for admin-only access."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class BlockedIPViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blocked IP addresses.
    
    list: Get all blocked IPs
    create: Block a new IP address
    retrieve: Get details of a blocked IP
    destroy: Unblock an IP address
    """
    queryset = BlockedIP.objects.all()
    serializer_class = BlockedIPSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['reason', 'is_permanent']
    search_fields = ['ip_address', 'description']
    ordering_fields = ['blocked_at', 'expires_at']
    
    @swagger_auto_schema(
        operation_description="Block a new IP address",
        request_body=BlockIPRequestSerializer,
        responses={201: BlockedIPSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = BlockIPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blocked_ip = BlockedIP.block_ip(
            ip_address=serializer.validated_data['ip_address'],
            reason=serializer.validated_data['reason'],
            duration_hours=serializer.validated_data.get('duration_hours', 24),
            description=serializer.validated_data.get('description'),
            blocked_by=request.user,
            permanent=serializer.validated_data.get('permanent', False)
        )
        
        # Clear cache
        cache.delete(f"ip_blocklist:{blocked_ip.ip_address}")
        
        return Response(
            BlockedIPSerializer(blocked_ip).data,
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ip_address = instance.ip_address
        
        self.perform_destroy(instance)
        
        # Clear cache
        cache.delete(f"ip_blocklist:{ip_address}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="Check if an IP is blocked",
        manual_parameters=[
            openapi.Parameter('ip', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ]
    )
    @action(detail=False, methods=['get'])
    def check(self, request):
        """Check if a specific IP is blocked."""
        ip_address = request.query_params.get('ip')
        if not ip_address:
            return Response(
                {'error': 'IP address required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_blocked = BlockedIP.is_blocked(ip_address)
        blocked_info = None
        
        if is_blocked:
            try:
                blocked = BlockedIP.objects.get(ip_address=ip_address)
                blocked_info = BlockedIPSerializer(blocked).data
            except BlockedIP.DoesNotExist:
                pass
        
        return Response({
            'ip_address': ip_address,
            'is_blocked': is_blocked,
            'details': blocked_info
        })


class AllowedIPViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whitelisted IP addresses."""
    queryset = AllowedIP.objects.all()
    serializer_class = AllowedIPSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['ip_address', 'description']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
        # Clear whitelist cache
        cache.delete(f"ip_whitelist:{serializer.instance.ip_address}")
    
    def perform_destroy(self, instance):
        ip_address = instance.ip_address
        instance.delete()
        cache.delete(f"ip_whitelist:{ip_address}")


class IPAccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing IP access logs (read-only)."""
    queryset = IPAccessLog.objects.all()
    serializer_class = IPAccessLogSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['is_suspicious', 'method', 'status_code']
    search_fields = ['ip_address', 'endpoint', 'user_agent']
    ordering_fields = ['timestamp', 'response_time_ms', 'threat_score']
    
    @swagger_auto_schema(
        operation_description="Get logs for a specific IP address",
        manual_parameters=[
            openapi.Parameter('ip', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('days', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, default=7)
        ]
    )
    @action(detail=False, methods=['get'])
    def by_ip(self, request):
        """Get access logs for a specific IP."""
        ip_address = request.query_params.get('ip')
        days = int(request.query_params.get('days', 7))
        
        if not ip_address:
            return Response(
                {'error': 'IP address required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cutoff = timezone.now() - timedelta(days=days)
        logs = self.queryset.filter(
            ip_address=ip_address,
            timestamp__gte=cutoff
        )
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def suspicious(self, request):
        """Get all suspicious requests."""
        logs = self.queryset.filter(is_suspicious=True)[:100]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class SecurityAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing security alerts."""
    queryset = SecurityAlert.objects.all()
    serializer_class = SecurityAlertSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['alert_type', 'severity', 'is_resolved']
    search_fields = ['title', 'description', 'ip_address']
    ordering_fields = ['created_at', 'severity']
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved."""
        alert = self.get_object()
        alert.resolve(request.user)
        return Response(self.get_serializer(alert).data)
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved alerts."""
        alerts = self.queryset.filter(is_resolved=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get all critical severity alerts."""
        alerts = self.queryset.filter(severity='critical', is_resolved=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class SecurityDashboardView(APIView):
    """
    Security dashboard with aggregated metrics.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get security dashboard metrics",
        responses={200: SecurityDashboardSerializer}
    )
    def get(self, request):
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Get metrics
        blocked_ips_count = BlockedIP.objects.filter(
            is_permanent=True
        ).count() + BlockedIP.objects.filter(
            is_permanent=False,
            expires_at__gt=now
        ).count()
        
        recent_alerts = SecurityAlert.objects.filter(
            created_at__gte=last_24h
        ).count()
        
        unresolved_alerts = SecurityAlert.objects.filter(
            is_resolved=False
        ).count()
        
        suspicious_requests = IPAccessLog.objects.filter(
            is_suspicious=True,
            timestamp__gte=last_24h
        ).count()
        
        failed_logins = LoginAttempt.objects.filter(
            was_successful=False,
            timestamp__gte=last_24h
        ).count()
        
        # Top blocked IPs
        top_blocked = BlockedIP.objects.values('reason').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Request trends (last 7 days)
        request_trends = IPAccessLog.objects.filter(
            timestamp__gte=last_7d
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id'),
            suspicious_count=Count('id', filter=models.Q(is_suspicious=True))
        ).order_by('date')
        
        # Recent alerts list
        recent_alerts_list = SecurityAlert.objects.filter(
            created_at__gte=last_24h
        ).order_by('-created_at')[:10]
        
        data = {
            'summary': {
                'blocked_ips': blocked_ips_count,
                'alerts_24h': recent_alerts,
                'unresolved_alerts': unresolved_alerts,
                'suspicious_requests_24h': suspicious_requests,
                'failed_logins_24h': failed_logins,
            },
            'blocked_by_reason': list(top_blocked),
            'request_trends': list(request_trends),
            'recent_alerts': SecurityAlertSerializer(recent_alerts_list, many=True).data,
        }
        
        return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def my_ip(request):
    """Get the client's IP address (useful for testing)."""
    ip_address = get_client_ip(request)
    return Response({
        'ip_address': ip_address,
        'is_blocked': BlockedIP.is_blocked(ip_address),
        'is_whitelisted': AllowedIP.is_whitelisted(ip_address)
    })


# Import models for the dashboard
from django.db import models
