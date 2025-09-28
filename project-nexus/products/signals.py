# products/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from .tasks import update_product_cache
from core.cache_utils import CacheManager

@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    """Signal to handle product cache updates"""
    update_product_cache.delay(instance.id)

@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    """Signal to handle product cache invalidation"""
    CacheManager.invalidate_product_cache(instance.id)