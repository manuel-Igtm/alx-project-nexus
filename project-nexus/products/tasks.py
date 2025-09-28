# products/tasks.py
from celery import shared_task
from django.core.cache import cache

@shared_task
def update_product_cache(product_id):
    """Update product cache asynchronously"""
    # Import inside function to avoid circular imports
    from .models import Product
    from .serializers import ProductSerializer
    from core.cache_utils import CacheManager
    
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        CacheManager.cache_product(serializer.data)
        return f"Cache updated for product {product_id}"
    except Product.DoesNotExist:
        return f"Product {product_id} not found"

@shared_task
def clear_category_cache(category_id):
    """Clear category-related cache"""
    from core.cache_utils import invalidate_cache_pattern
    invalidate_cache_pattern(f"category_products:{category_id}")
    invalidate_cache_pattern("featured_products")

@shared_task
def send_low_stock_notification(product_id):
    """Send notification when product stock is low"""
    from .models import Product
    try:
        product = Product.objects.get(id=product_id)
        if product.stock < 10:  # Low stock threshold
            print(f"Low stock alert for {product.name}: {product.stock} remaining")
            # In real app, send email/notification here
        return f"Stock check completed for {product.name}"
    except Product.DoesNotExist:
        return f"Product {product_id} not found"