"""
URL configuration for Project Nexus E-Commerce API.

Provides REST API endpoints, GraphQL, and interactive documentation.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static

from graphene_django.views import GraphQLView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views import health_check


# =============================================================================
# API DOCUMENTATION CONFIGURATION
# =============================================================================

schema_view = get_schema_view(
    openapi.Info(
        title="🚀 Project Nexus E-Commerce API",
        default_version='v1.0.0',
        description="""
# Welcome to Project Nexus API

A powerful, secure, and scalable e-commerce backend API built with Django REST Framework.

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** for authentication. 

### Getting Started:
1. **Register** a new account at `/api/auth/register/`
2. **Login** to get your tokens at `/api/auth/login/`
3. Include the access token in your requests: `Authorization: Bearer <your_access_token>`
4. **Refresh** your token at `/api/auth/token/refresh/` when it expires

---

## 📦 Core Features

- **Products & Categories**: Browse products with filtering, search, and pagination
- **Shopping Cart**: Add/remove items, guest cart support
- **Orders & Checkout**: Order creation and management
- **Payments**: Multiple payment methods (Chapa, M-Pesa)
- **Notifications**: Real-time updates

---

## 🛡️ Security Features

- **IP Blocking**: Automatic detection and blocking of malicious IPs
- **Rate Limiting**: Protection against API abuse
- **Brute Force Protection**: Automatic lockout after failed attempts
        """,
        terms_of_service="https://www.projectnexus.com/terms/",
        contact=openapi.Contact(
            name="API Support",
            email="api-support@projectnexus.com",
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# =============================================================================
# ROOT VIEW
# =============================================================================

def api_root(request):
    """API root endpoint with overview information."""
    return JsonResponse({
        "name": "Project Nexus E-Commerce API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs/",
            "redoc": "/redoc/",
            "graphql": "/graphql/",
        },
        "endpoints": {
            "api": "/api/",
            "auth": "/api/auth/",
            "products": "/api/products/",
            "categories": "/api/categories/",
            "orders": "/api/orders/",
            "cart": "/api/carts/",
            "payments": "/api/payments/",
            "notifications": "/api/notifications/",
            "security": "/api/security/",
        },
    })


# =============================================================================
# URL PATTERNS
# =============================================================================

urlpatterns = [
    # Root
    path('', api_root, name='api-root'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include('api.urls')),
    path('api/security/', include('security.urls')),
    
    # GraphQL
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True)), name='graphql'),
    
    # Documentation - Swagger UI
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Documentation - ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Health check
    path('health/', health_check, name='health-check'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# =============================================================================
# ADMIN CUSTOMIZATION
# =============================================================================

admin.site.site_header = "Project Nexus Admin"
admin.site.site_title = "Project Nexus E-Commerce"
admin.site.index_title = "Dashboard"

