from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import action
from core.cache_utils import cache_result, CacheManager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings


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
    
    @cache_result(ttl=600, key_prefix='products_list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        
        # Try to get from cache first
        cached_product = CacheManager.get_cached_product(product_id)
        if cached_product:
            return Response(cached_product)
        
        # If not in cache, get from database and cache it
        response = super().retrieve(request, *args, **kwargs)
        CacheManager.cache_product(response.data)
        
        return response
    
    def perform_create(self, serializer):
        instance = serializer.save()
        # Invalidate relevant caches
        CacheManager.invalidate_product_cache(instance.id)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        # Invalidate relevant caches
        CacheManager.invalidate_product_cache(instance.id)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products with caching"""
        cache_key = CacheManager.get_featured_products_key()
        featured_products = cache.get(cache_key)
        
        if not featured_products:
            featured_products = self.queryset.filter(
                is_featured=True, 
                is_active=True
            )[:10]
            serializer = self.get_serializer(featured_products, many=True)
            featured_products = serializer.data
            cache.set(cache_key, featured_products, 3600)  # Cache for 1 hour
        
        return Response(featured_products)

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


@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=['HS256']
        )
        
        # Generate new access token
        new_access_token = jwt.encode(
            {'user_id': payload['user_id']},
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return Response({
            'access_token': new_access_token
        })
        
    except jwt.ExpiredSignatureError:
        return Response(
            {'error': 'Refresh token expired'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    except jwt.InvalidTokenError:
        return Response(
            {'error': 'Invalid refresh token'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )