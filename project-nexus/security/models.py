from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class BlockedIP(models.Model):
    """Model for storing blocked IP addresses."""
    
    BLOCK_REASON_CHOICES = (
        ('rate_limit', 'Rate Limit Exceeded'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('brute_force', 'Brute Force Attack'),
        ('spam', 'Spam Detection'),
        ('manual', 'Manual Block'),
        ('geo_block', 'Geographic Restriction'),
    )
    
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    reason = models.CharField(max_length=50, choices=BLOCK_REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    blocked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    blocked_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='blocked_ips'
    )
    
    class Meta:
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
        ordering = ['-blocked_at']
    
    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"
    
    @property
    def is_active(self):
        """Check if the block is still active."""
        if self.is_permanent:
            return True
        if self.expires_at and self.expires_at > timezone.now():
            return True
        return False
    
    @classmethod
    def is_blocked(cls, ip_address):
        """Check if an IP address is currently blocked."""
        try:
            blocked = cls.objects.get(ip_address=ip_address)
            if blocked.is_active:
                return True
            # Clean up expired blocks
            if not blocked.is_permanent and blocked.expires_at and blocked.expires_at <= timezone.now():
                blocked.delete()
            return False
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def block_ip(cls, ip_address, reason, duration_hours=24, description=None, blocked_by=None, permanent=False):
        """Block an IP address."""
        expires_at = None if permanent else timezone.now() + timedelta(hours=duration_hours)
        
        blocked, created = cls.objects.update_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'description': description,
                'expires_at': expires_at,
                'is_permanent': permanent,
                'blocked_by': blocked_by,
            }
        )
        return blocked


class AllowedIP(models.Model):
    """Model for whitelisted IP addresses."""
    
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whitelisted_ips'
    )
    
    class Meta:
        verbose_name = 'Allowed IP'
        verbose_name_plural = 'Allowed IPs'
    
    def __str__(self):
        return self.ip_address
    
    @classmethod
    def is_whitelisted(cls, ip_address):
        """Check if an IP is whitelisted."""
        return cls.objects.filter(ip_address=ip_address).exists()


class IPAccessLog(models.Model):
    """Model for tracking IP access logs."""
    
    ip_address = models.GenericIPAddressField(db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_logs'
    )
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    request_data = models.JSONField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Geolocation data (optional)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    # Threat detection
    is_suspicious = models.BooleanField(default=False)
    threat_score = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'IP Access Log'
        verbose_name_plural = 'IP Access Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['is_suspicious', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.ip_address} - {self.endpoint} - {self.timestamp}"


class LoginAttempt(models.Model):
    """Track login attempts for brute force detection."""
    
    ip_address = models.GenericIPAddressField(db_index=True)
    email = models.EmailField(blank=True, null=True)
    was_successful = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['email', 'timestamp']),
        ]
    
    def __str__(self):
        status = "Success" if self.was_successful else "Failed"
        return f"{self.ip_address} - {status} - {self.timestamp}"
    
    @classmethod
    def get_failed_attempts(cls, ip_address, minutes=30):
        """Get failed login attempts in the last N minutes."""
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            was_successful=False,
            timestamp__gte=cutoff
        ).count()


class SecurityAlert(models.Model):
    """Model for security alerts and incidents."""
    
    SEVERITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    ALERT_TYPE_CHOICES = (
        ('brute_force', 'Brute Force Attack'),
        ('rate_limit', 'Rate Limit Breach'),
        ('suspicious_pattern', 'Suspicious Pattern'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_breach', 'Potential Data Breach'),
        ('injection_attempt', 'Injection Attempt'),
    )
    
    ip_address = models.GenericIPAddressField(db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_alerts'
    )
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.title}"
    
    def resolve(self, user):
        """Mark alert as resolved."""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()
