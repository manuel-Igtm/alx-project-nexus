# api/schema.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

# Common parameters
product_id_parameter = openapi.Parameter(
    'id', 
    openapi.IN_PATH, 
    description="Product ID", 
    type=openapi.TYPE_INTEGER
)

category_id_parameter = openapi.Parameter(
    'id',
    openapi.IN_PATH,
    description="Category ID",
    type=openapi.TYPE_INTEGER
)

order_id_parameter = openapi.Parameter(
    'id',
    openapi.IN_PATH,
    description="Order ID",
    type=openapi.TYPE_INTEGER
)

# Request/Response schemas
product_create_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name', 'price', 'category'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='Product name'),
        'description': openapi.Schema(type=openapi.TYPE_STRING, description='Product description'),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Product price'),
        'stock': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stock quantity'),
        'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='Category ID'),
        'is_featured': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Featured product flag'),
    }
)

order_create_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['items'],
    properties={
        'items': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'product': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        'shipping_address': openapi.Schema(type=openapi.TYPE_STRING),
        'billing_address': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

# Response schemas
product_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'stock': openapi.Schema(type=openapi.TYPE_INTEGER),
        'category': openapi.Schema(type=openapi.TYPE_OBJECT),
        'is_featured': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING),
        'details': openapi.Schema(type=openapi.TYPE_OBJECT),
    }
)