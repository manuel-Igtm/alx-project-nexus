"""
Security Module Tests
Tests for IP blocking, rate limiting, and security features.
"""
import pytest
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from security.models import BlockedIP, AllowedIP, IPAccessLog, LoginAttempt, SecurityAlert
from security.middleware import (
    get_client_ip, IPBlockingMiddleware, RateLimitMiddleware,
    BruteForceProtectionMiddleware
)

User = get_user_model()


class TestBlockedIPModel(TestCase):
    """Tests for the BlockedIP model."""
    
    def test_create_blocked_ip(self):
        """Test creating a blocked IP."""
        blocked = BlockedIP.objects.create(
            ip_address='192.168.1.100',
            reason='rate_limit',
            description='Test block'
        )
        self.assertEqual(str(blocked), '192.168.1.100 - Rate Limit Exceeded')
    
    def test_permanent_block(self):
        """Test permanent IP block."""
        blocked = BlockedIP.block_ip(
            ip_address='192.168.1.101',
            reason='brute_force',
            permanent=True
        )
        self.assertTrue(blocked.is_permanent)
        self.assertTrue(blocked.is_active)
    
    def test_temporary_block_expires(self):
        """Test that temporary blocks expire."""
        blocked = BlockedIP.block_ip(
            ip_address='192.168.1.102',
            reason='spam',
            duration_hours=1
        )
        self.assertFalse(blocked.is_permanent)
        self.assertTrue(blocked.is_active)
        
        # Simulate expiration
        blocked.expires_at = timezone.now() - timedelta(hours=1)
        blocked.save()
        self.assertFalse(blocked.is_active)
    
    def test_is_blocked_check(self):
        """Test the is_blocked class method."""
        ip = '192.168.1.103'
        self.assertFalse(BlockedIP.is_blocked(ip))
        
        BlockedIP.block_ip(ip, 'manual', permanent=True)
        self.assertTrue(BlockedIP.is_blocked(ip))


class TestAllowedIPModel(TestCase):
    """Tests for the AllowedIP model."""
    
    def test_create_allowed_ip(self):
        """Test creating an allowed IP."""
        allowed = AllowedIP.objects.create(
            ip_address='10.0.0.1',
            description='Office IP'
        )
        self.assertEqual(str(allowed), '10.0.0.1')
    
    def test_is_whitelisted(self):
        """Test the is_whitelisted class method."""
        ip = '10.0.0.2'
        self.assertFalse(AllowedIP.is_whitelisted(ip))
        
        AllowedIP.objects.create(ip_address=ip)
        self.assertTrue(AllowedIP.is_whitelisted(ip))


class TestSecurityAlertModel(TestCase):
    """Tests for the SecurityAlert model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123'
        )
    
    def test_create_alert(self):
        """Test creating a security alert."""
        alert = SecurityAlert.objects.create(
            ip_address='192.168.1.200',
            alert_type='brute_force',
            severity='high',
            title='Brute force attack detected',
            description='Multiple failed login attempts'
        )
        self.assertFalse(alert.is_resolved)
    
    def test_resolve_alert(self):
        """Test resolving a security alert."""
        alert = SecurityAlert.objects.create(
            ip_address='192.168.1.201',
            alert_type='rate_limit',
            severity='medium',
            title='Rate limit exceeded',
            description='Too many requests'
        )
        alert.resolve(self.user)
        
        self.assertTrue(alert.is_resolved)
        self.assertEqual(alert.resolved_by, self.user)
        self.assertIsNotNone(alert.resolved_at)


class TestGetClientIP(TestCase):
    """Tests for the get_client_ip helper function."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_direct_ip(self):
        """Test getting IP from REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        self.assertEqual(get_client_ip(request), '192.168.1.1')
    
    def test_forwarded_ip(self):
        """Test getting IP from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 70.41.3.18'
        self.assertEqual(get_client_ip(request), '203.0.113.1')


class TestIPAccessLogModel(TestCase):
    """Tests for the IPAccessLog model."""
    
    def test_create_access_log(self):
        """Test creating an access log entry."""
        log = IPAccessLog.objects.create(
            ip_address='192.168.1.50',
            endpoint='/api/products/',
            method='GET',
            status_code=200,
            response_time_ms=45
        )
        self.assertFalse(log.is_suspicious)
    
    def test_suspicious_log(self):
        """Test creating a suspicious access log."""
        log = IPAccessLog.objects.create(
            ip_address='192.168.1.51',
            endpoint='/api/admin/',
            method='POST',
            status_code=403,
            is_suspicious=True,
            threat_score=75
        )
        self.assertTrue(log.is_suspicious)
        self.assertEqual(log.threat_score, 75)


class TestLoginAttemptModel(TestCase):
    """Tests for the LoginAttempt model."""
    
    def test_record_failed_attempt(self):
        """Test recording a failed login attempt."""
        attempt = LoginAttempt.objects.create(
            ip_address='192.168.1.60',
            email='user@test.com',
            was_successful=False
        )
        self.assertFalse(attempt.was_successful)
    
    def test_get_failed_attempts_count(self):
        """Test counting failed attempts."""
        ip = '192.168.1.61'
        
        # Create 5 failed attempts
        for _ in range(5):
            LoginAttempt.objects.create(
                ip_address=ip,
                was_successful=False
            )
        
        # Create 1 successful attempt
        LoginAttempt.objects.create(
            ip_address=ip,
            was_successful=True
        )
        
        failed_count = LoginAttempt.get_failed_attempts(ip, minutes=30)
        self.assertEqual(failed_count, 5)


@pytest.mark.security
class TestSecurityMiddlewareIntegration(TestCase):
    """Integration tests for security middleware."""
    
    def test_blocked_ip_returns_403(self):
        """Test that blocked IPs receive 403 response."""
        # Block an IP
        BlockedIP.block_ip('203.0.113.50', 'manual', permanent=True)
        
        # Make request with blocked IP (follow redirects to get final response)
        response = self.client.get(
            '/health/',
            HTTP_X_FORWARDED_FOR='203.0.113.50',
            follow=True
        )
        
        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
        self.assertIn('IP_BLOCKED', str(response.content))
    
    def test_whitelisted_ip_bypasses_block(self):
        """Test that whitelisted IPs bypass blocking."""
        ip = '203.0.113.51'
        
        # Whitelist the IP
        AllowedIP.objects.create(ip_address=ip)
        
        # Also block the IP
        BlockedIP.block_ip(ip, 'manual', permanent=True)
        
        # Make request - should succeed because IP is whitelisted (follow redirects)
        response = self.client.get(
            '/health/',
            HTTP_X_FORWARDED_FOR=ip,
            follow=True
        )
        
        self.assertEqual(response.status_code, 200)

