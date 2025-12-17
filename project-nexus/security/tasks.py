from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='security.log_access_async')
def log_access_async(ip_address, user_id, endpoint, method, status_code, 
                     user_agent, response_time_ms, is_suspicious):
    """Asynchronously log access requests."""
    try:
        from security.models import IPAccessLog
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = None
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        IPAccessLog.objects.create(
            ip_address=ip_address,
            user=user,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            user_agent=user_agent,
            response_time_ms=response_time_ms,
            is_suspicious=is_suspicious
        )
    except Exception as e:
        logger.error(f"Failed to log access: {e}")


@shared_task(name='security.cleanup_expired_blocks')
def cleanup_expired_blocks():
    """Remove expired IP blocks."""
    try:
        from security.models import BlockedIP
        
        expired = BlockedIP.objects.filter(
            is_permanent=False,
            expires_at__lte=timezone.now()
        )
        count = expired.count()
        expired.delete()
        
        logger.info(f"Cleaned up {count} expired IP blocks")
        return count
    except Exception as e:
        logger.error(f"Failed to cleanup expired blocks: {e}")
        return 0


@shared_task(name='security.cleanup_old_logs')
def cleanup_old_logs(days=30):
    """Remove access logs older than specified days."""
    try:
        from security.models import IPAccessLog, LoginAttempt
        
        cutoff = timezone.now() - timedelta(days=days)
        
        # Clean access logs
        access_count = IPAccessLog.objects.filter(timestamp__lt=cutoff).delete()[0]
        
        # Clean login attempts (keep for shorter time)
        login_cutoff = timezone.now() - timedelta(days=7)
        login_count = LoginAttempt.objects.filter(timestamp__lt=login_cutoff).delete()[0]
        
        logger.info(f"Cleaned up {access_count} access logs and {login_count} login attempts")
        return {'access_logs': access_count, 'login_attempts': login_count}
    except Exception as e:
        logger.error(f"Failed to cleanup old logs: {e}")
        return {'error': str(e)}


@shared_task(name='security.analyze_suspicious_activity')
def analyze_suspicious_activity():
    """Analyze logs for suspicious patterns and create alerts."""
    try:
        from security.models import IPAccessLog, SecurityAlert, BlockedIP
        from django.db.models import Count
        
        last_hour = timezone.now() - timedelta(hours=1)
        
        # Find IPs with many suspicious requests
        suspicious_ips = IPAccessLog.objects.filter(
            is_suspicious=True,
            timestamp__gte=last_hour
        ).values('ip_address').annotate(
            count=Count('id')
        ).filter(count__gte=10)
        
        alerts_created = 0
        
        for entry in suspicious_ips:
            ip = entry['ip_address']
            count = entry['count']
            
            # Check if alert already exists
            existing = SecurityAlert.objects.filter(
                ip_address=ip,
                alert_type='suspicious_pattern',
                is_resolved=False,
                created_at__gte=last_hour
            ).exists()
            
            if not existing:
                SecurityAlert.objects.create(
                    ip_address=ip,
                    alert_type='suspicious_pattern',
                    severity='medium',
                    title=f'Suspicious activity pattern from {ip}',
                    description=f'Detected {count} suspicious requests in the last hour.'
                )
                alerts_created += 1
                
                # Auto-block if very suspicious
                if count >= 50:
                    BlockedIP.block_ip(
                        ip_address=ip,
                        reason='suspicious_activity',
                        duration_hours=6,
                        description=f'Auto-blocked after {count} suspicious requests'
                    )
        
        logger.info(f"Created {alerts_created} security alerts")
        return alerts_created
    except Exception as e:
        logger.error(f"Failed to analyze suspicious activity: {e}")
        return 0


@shared_task(name='security.send_security_report')
def send_security_report():
    """Send daily security report (placeholder for email integration)."""
    try:
        from security.models import SecurityAlert, BlockedIP, IPAccessLog
        
        last_24h = timezone.now() - timedelta(hours=24)
        
        report = {
            'new_alerts': SecurityAlert.objects.filter(created_at__gte=last_24h).count(),
            'unresolved_alerts': SecurityAlert.objects.filter(is_resolved=False).count(),
            'critical_alerts': SecurityAlert.objects.filter(
                severity='critical',
                is_resolved=False
            ).count(),
            'new_blocks': BlockedIP.objects.filter(blocked_at__gte=last_24h).count(),
            'suspicious_requests': IPAccessLog.objects.filter(
                is_suspicious=True,
                timestamp__gte=last_24h
            ).count(),
        }
        
        logger.info(f"Security report: {report}")
        
        # TODO: Send email with report
        # send_mail(...)
        
        return report
    except Exception as e:
        logger.error(f"Failed to generate security report: {e}")
        return {'error': str(e)}
