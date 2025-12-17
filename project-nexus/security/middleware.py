import time
import logging
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Extract client IP from request, handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def safe_cache_get(key, default=None):
    """Safely get from cache, handling connection errors."""
    try:
        return cache.get(key, default)
    except Exception as e:
        logger.warning(f"Cache get failed for {key}: {e}")
        return default


def safe_cache_set(key, value, timeout=None):
    """Safely set to cache, handling connection errors."""
    try:
        cache.set(key, value, timeout)
    except Exception as e:
        logger.warning(f"Cache set failed for {key}: {e}")


class IPBlockingMiddleware:
    """
    Middleware to block requests from blocked IP addresses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Lazy import to avoid circular imports
        self.BlockedIP = None
        self.AllowedIP = None
    
    def _get_models(self):
        if self.BlockedIP is None:
            from security.models import BlockedIP, AllowedIP
            self.BlockedIP = BlockedIP
            self.AllowedIP = AllowedIP
    
    def __call__(self, request):
        self._get_models()
        
        ip_address = get_client_ip(request)
        
        # Check whitelist first (cached)
        whitelist_key = f"ip_whitelist:{ip_address}"
        is_whitelisted = safe_cache_get(whitelist_key)
        
        if is_whitelisted is None:
            is_whitelisted = self.AllowedIP.is_whitelisted(ip_address)
            safe_cache_set(whitelist_key, is_whitelisted, timeout=300)  # 5 min cache
        
        if not is_whitelisted:
            # Check blocklist (cached)
            blocklist_key = f"ip_blocklist:{ip_address}"
            is_blocked = safe_cache_get(blocklist_key)
            
            if is_blocked is None:
                is_blocked = self.BlockedIP.is_blocked(ip_address)
                safe_cache_set(blocklist_key, is_blocked, timeout=60)  # 1 min cache
            
            if is_blocked:
                logger.warning(f"Blocked request from IP: {ip_address}")
                return JsonResponse({
                    'error': 'Access denied',
                    'message': 'Your IP address has been blocked due to security concerns.',
                    'code': 'IP_BLOCKED'
                }, status=403)
        
        response = self.get_response(request)
        return response


class RateLimitMiddleware:
    """
    Middleware for rate limiting requests per IP.
    """
    
    # Rate limits: (requests, seconds)
    RATE_LIMITS = {
        'default': (100, 60),      # 100 requests per minute
        'auth': (10, 60),          # 10 auth requests per minute
        'api': (200, 60),          # 200 API requests per minute
    }
    
    AUTH_PATHS = ['/api/auth/', '/api/login/', '/api/register/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        ip_address = get_client_ip(request)
        path = request.path
        
        # Determine rate limit category
        if any(path.startswith(auth_path) for auth_path in self.AUTH_PATHS):
            limit, window = self.RATE_LIMITS['auth']
            category = 'auth'
        elif path.startswith('/api/'):
            limit, window = self.RATE_LIMITS['api']
            category = 'api'
        else:
            limit, window = self.RATE_LIMITS['default']
            category = 'default'
        
        cache_key = f"rate_limit:{category}:{ip_address}"
        
        # Get current request count (with safe fallback)
        current = safe_cache_get(cache_key, 0)
        
        if current >= limit:
            # Check if we should auto-block
            self._handle_rate_limit_exceeded(ip_address, category)
            
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Please wait before trying again.',
                'retry_after': window,
                'code': 'RATE_LIMIT_EXCEEDED'
            }, status=429, headers={'Retry-After': str(window)})
        
        # Increment counter (with safe fallback)
        try:
            if current == 0:
                cache.set(cache_key, 1, timeout=window)
            else:
                cache.incr(cache_key)
        except Exception as e:
            logger.warning(f"Failed to update rate limit counter: {e}")
        
        response = self.get_response(request)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Remaining'] = str(max(0, limit - current - 1))
        response['X-RateLimit-Reset'] = str(window)
        
        return response
    
    def _handle_rate_limit_exceeded(self, ip_address, category):
        """Handle repeated rate limit violations."""
        violation_key = f"rate_violations:{ip_address}"
        violations = safe_cache_get(violation_key, 0)
        
        if violations >= 5:
            # Auto-block after 5 violations
            try:
                from security.models import BlockedIP
                BlockedIP.block_ip(
                    ip_address=ip_address,
                    reason='rate_limit',
                    duration_hours=1,
                    description=f'Auto-blocked after repeated rate limit violations in {category}'
                )
                safe_cache_set(violation_key, 0, timeout=1)  # Reset
                logger.warning(f"Auto-blocked IP {ip_address} for rate limit violations")
            except Exception as e:
                logger.error(f"Failed to auto-block IP {ip_address}: {e}")
        else:
            safe_cache_set(violation_key, violations + 1, timeout=3600)  # 1 hour window


class SecurityLoggingMiddleware:
    """
    Middleware to log requests for security monitoring.
    """
    
    # Paths to exclude from logging
    EXCLUDE_PATHS = ['/health/', '/static/', '/media/', '/favicon.ico']
    
    # Sensitive paths to always log
    SENSITIVE_PATHS = ['/admin/', '/api/auth/', '/api/payments/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDE_PATHS):
            return self.get_response(request)
        
        start_time = time.time()
        ip_address = get_client_ip(request)
        
        response = self.get_response(request)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log to database asynchronously for sensitive paths or suspicious requests
        should_log = (
            any(request.path.startswith(path) for path in self.SENSITIVE_PATHS) or
            response.status_code >= 400 or
            self._is_suspicious_request(request)
        )
        
        if should_log:
            self._log_request(request, response, ip_address, response_time_ms)
        
        return response
    
    def _is_suspicious_request(self, request):
        """Detect potentially suspicious requests."""
        suspicious_patterns = [
            'SELECT', 'UNION', 'INSERT', 'DELETE', 'DROP',  # SQL injection
            '<script>', 'javascript:', 'onerror=',  # XSS
            '../', '..\\', '%2e%2e',  # Path traversal
            'eval(', 'exec(', '__import__',  # Code injection
        ]
        
        # Check query string
        query_string = request.META.get('QUERY_STRING', '').upper()
        
        # Check request body for POST/PUT
        body = ''
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.body.decode('utf-8', errors='ignore').upper()
            except:
                pass
        
        combined = query_string + body
        
        for pattern in suspicious_patterns:
            if pattern in combined:
                return True
        
        return False
    
    def _log_request(self, request, response, ip_address, response_time_ms):
        """Log request to database."""
        try:
            from security.models import IPAccessLog
            from security.tasks import log_access_async
            
            # Use Celery task if available
            if hasattr(settings, 'CELERY_BROKER_URL'):
                log_access_async.delay(
                    ip_address=ip_address,
                    user_id=request.user.id if request.user.is_authenticated else None,
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    response_time_ms=response_time_ms,
                    is_suspicious=self._is_suspicious_request(request)
                )
            else:
                # Synchronous logging
                IPAccessLog.objects.create(
                    ip_address=ip_address,
                    user=request.user if request.user.is_authenticated else None,
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    response_time_ms=response_time_ms,
                    is_suspicious=self._is_suspicious_request(request)
                )
        except Exception as e:
            logger.error(f"Failed to log request: {e}")


class BruteForceProtectionMiddleware:
    """
    Middleware to detect and prevent brute force attacks.
    """
    
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 1800  # 30 minutes in seconds
    
    AUTH_ENDPOINTS = ['/api/auth/login/', '/api/auth/register/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Only check POST requests to auth endpoints
        if request.method != 'POST':
            return self.get_response(request)
        
        if not any(request.path.startswith(ep) for ep in self.AUTH_ENDPOINTS):
            return self.get_response(request)
        
        ip_address = get_client_ip(request)
        lockout_key = f"bruteforce_lockout:{ip_address}"
        
        # Check if IP is locked out (with safe fallback)
        if safe_cache_get(lockout_key):
            return JsonResponse({
                'error': 'Account temporarily locked',
                'message': 'Too many failed attempts. Please try again later.',
                'code': 'ACCOUNT_LOCKED'
            }, status=429)
        
        response = self.get_response(request)
        
        # Track failed attempts
        if response.status_code in [400, 401, 403]:
            self._record_failed_attempt(ip_address, request)
        elif response.status_code in [200, 201]:
            # Clear failed attempts on success
            try:
                cache.delete(f"failed_attempts:{ip_address}")
            except Exception:
                pass
        
        return response
    
    def _record_failed_attempt(self, ip_address, request):
        """Record a failed login attempt."""
        attempt_key = f"failed_attempts:{ip_address}"
        attempts = safe_cache_get(attempt_key, 0) + 1
        
        safe_cache_set(attempt_key, attempts, timeout=self.LOCKOUT_DURATION)
        
        if attempts >= self.MAX_FAILED_ATTEMPTS:
            # Lock out the IP
            lockout_key = f"bruteforce_lockout:{ip_address}"
            safe_cache_set(lockout_key, True, timeout=self.LOCKOUT_DURATION)
            
            # Log the incident
            try:
                from security.models import LoginAttempt, SecurityAlert, BlockedIP
                
                # Create security alert
                SecurityAlert.objects.create(
                    ip_address=ip_address,
                    alert_type='brute_force',
                    severity='high',
                    title=f'Brute force attack detected from {ip_address}',
                    description=f'IP {ip_address} has been locked out after {attempts} failed login attempts.'
                )
                
                # Auto-block after multiple lockouts
                lockout_count_key = f"lockout_count:{ip_address}"
                lockout_count = safe_cache_get(lockout_count_key, 0) + 1
                safe_cache_set(lockout_count_key, lockout_count, timeout=86400)  # 24 hours
                
                if lockout_count >= 3:
                    BlockedIP.block_ip(
                        ip_address=ip_address,
                        reason='brute_force',
                        duration_hours=24,
                        description='Auto-blocked after multiple brute force lockouts'
                    )
                    
            except Exception as e:
                logger.error(f"Failed to record brute force attempt: {e}")
