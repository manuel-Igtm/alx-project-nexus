
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import UserProfile

def user_profile(request, user_id):
    cache_key = f"user_profile_{user_id}"
    profile = cache.get(cache_key)

    if not profile:
        profile = get_object_or_404(UserProfile, pk=user_id)
        profile = {"id": profile.id, "username": profile.user.username, "email": profile.user.email}
        cache.set(cache_key, profile, timeout=60*10)  # Cache 10 mins

    return JsonResponse(profile)
