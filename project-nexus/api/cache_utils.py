
from django.core.cache import cache
from functools import wraps

def cache_result(ttl=300, key_prefix='cache'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(kwargs)}"
            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator