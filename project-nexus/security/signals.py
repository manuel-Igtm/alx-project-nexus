from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import BlockedIP, AllowedIP
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BlockedIP)
def clear_blocklist_cache(sender, instance, **kwargs):
    """Clear blocklist cache when a BlockedIP is created or updated."""
    try:
        cache_key = f"ip_blocklist:{instance.ip_address}"
        cache.delete(cache_key)
        logger.debug(f"Cleared blocklist cache for {instance.ip_address}")
    except Exception as e:
        # Cache might not be available in some environments
        logger.warning(f"Failed to clear blocklist cache: {e}")


@receiver(post_save, sender=AllowedIP)
def clear_whitelist_cache(sender, instance, **kwargs):
    """Clear whitelist cache when an AllowedIP is created or updated."""
    try:
        cache_key = f"ip_whitelist:{instance.ip_address}"
        cache.delete(cache_key)
        logger.debug(f"Cleared whitelist cache for {instance.ip_address}")
    except Exception as e:
        # Cache might not be available in some environments
        logger.warning(f"Failed to clear whitelist cache: {e}")
