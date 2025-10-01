# products/views.py - KEEP ONLY THESE:
from django.core.cache import cache
from django.http import JsonResponse
from .models import Product, Category

def product_list(request):
    cache_key = "products_all"
    products = cache.get(cache_key)

    if not products:
        products = list(Product.objects.values("id", "name", "price", "category__name"))
        cache.set(cache_key, products, timeout=60*5)  # Cache for 5 mins

    return JsonResponse({"products": products})

def category_list(request):
    cache_key = "categories_all"
    categories = cache.get(cache_key)

    if not categories:
        categories = list(Category.objects.values("id", "name"))
        cache.set(cache_key, categories, timeout=60*30)  # Cache 30 mins

    return JsonResponse({"categories": categories})