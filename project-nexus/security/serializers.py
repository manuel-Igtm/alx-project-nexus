from rest_framework import serializers
from .models import BlockedIP, AllowedIP, IPAccessLog, LoginAttempt, SecurityAlert


class BlockedIPSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    blocked_by_username = serializers.CharField(source='blocked_by.email', read_only=True)
    
    class Meta:
        model = BlockedIP
        fields = [
            'id', 'ip_address', 'reason', 'description', 'blocked_at',
            'expires_at', 'is_permanent', 'is_active', 'blocked_by',
            'blocked_by_username'
        ]
        read_only_fields = ['blocked_at', 'blocked_by']


class BlockIPRequestSerializer(serializers.Serializer):
    ip_address = serializers.IPAddressField()
    reason = serializers.ChoiceField(choices=BlockedIP.BLOCK_REASON_CHOICES)
    description = serializers.CharField(required=False, allow_blank=True)
    duration_hours = serializers.IntegerField(min_value=1, max_value=8760, default=24)  # Max 1 year
    permanent = serializers.BooleanField(default=False)


class AllowedIPSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = AllowedIP
        fields = ['id', 'ip_address', 'description', 'created_at', 'created_by', 'created_by_username']
        read_only_fields = ['created_at', 'created_by']


class IPAccessLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = IPAccessLog
        fields = [
            'id', 'ip_address', 'user', 'user_email', 'endpoint', 'method',
            'status_code', 'user_agent', 'response_time_ms', 'timestamp',
            'country', 'city', 'is_suspicious', 'threat_score'
        ]


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = ['id', 'ip_address', 'email', 'was_successful', 'timestamp', 'user_agent']


class SecurityAlertSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.email', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = SecurityAlert
        fields = [
            'id', 'ip_address', 'user', 'user_email', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'title', 'description', 'is_resolved',
            'resolved_at', 'resolved_by', 'resolved_by_username', 'created_at'
        ]
        read_only_fields = ['resolved_at', 'resolved_by']


class SecurityDashboardSerializer(serializers.Serializer):
    """Serializer for API documentation of dashboard response."""
    summary = serializers.DictField()
    blocked_by_reason = serializers.ListField()
    request_trends = serializers.ListField()
    recent_alerts = SecurityAlertSerializer(many=True)
