from django.core.cache import cache
from django.conf import settings
import json
from functools import wraps

def cache_key_generator(key_prefix, *args, **kwargs):
    """Generate cache key with prefix and arguments"""
    key = key_prefix
    if args:
        key += f":{':'.join(str(arg) for arg in args)}"
    if kwargs:
        key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
    return key

def cache_result(ttl=300, key_prefix='cache'):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_key_generator(key_prefix, *args, **kwargs)
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def invalidate_cache_pattern(pattern):
    """Invalidate all cache keys matching a pattern"""
    keys = cache.keys(pattern)
    if keys:
        cache.delete_many(keys)

class CacheManager:
    """Cache manager for e-commerce specific caching"""
    
    @staticmethod
    def get_product_key(product_id):
        return f"product:{product_id}"
    
    @staticmethod
    def get_category_products_key(category_id):
        return f"category_products:{category_id}"
    
    @staticmethod
    def get_featured_products_key():
        return "featured_products"
    
    @staticmethod
    def get_user_cart_key(user_id):
        return f"user_cart:{user_id}"
    
    @staticmethod
    def cache_product(product_data):
        """Cache product data"""
        key = CacheManager.get_product_key(product_data['id'])
        cache.set(key, product_data, settings.CACHE_TTL)
    
    @staticmethod
    def get_cached_product(product_id):
        """Get cached product data"""
        key = CacheManager.get_product_key(product_id)
        return cache.get(key)
    
    @staticmethod
    def invalidate_product_cache(product_id):
        """Invalidate product cache"""
        key = CacheManager.get_product_key(product_id)
        cache.delete(key)
        # Also invalidate category listings that might include this product
        invalidate_cache_pattern("category_products:*")
        invalidate_cache_pattern("featured_products")