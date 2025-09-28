from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(active=True).prefetch_related("variants", "category")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug"]
    search_fields = ["name", "description"]
    ordering_fields = ["base_price", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# products/views.py --caching 
from django.core.cache import cache
from django.http import JsonResponse
from .models import Product

def product_list(request):
    cache_key = "products_all"
    products = cache.get(cache_key)

    if not products:
        products = list(Product.objects.values("id", "name", "price", "category__name"))
        cache.set(cache_key, products, timeout=60*5)  # Cache for 5 mins

    return JsonResponse({"products": products})


# categories
from django.core.cache import cache
from django.http import JsonResponse
from .models import Category

def category_list(request):
    cache_key = "categories_all"
    categories = cache.get(cache_key)

    if not categories:
        categories = list(Category.objects.values("id", "name"))
        cache.set(cache_key, categories, timeout=60*30)  # Cache 30 mins

    return JsonResponse({"categories": categories})

