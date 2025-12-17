# api/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product, Category
from orders.models import Order

class OrderModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            price=99.99,
            stock=10,
            category=self.category
        )
    
    def test_order_creation(self):
        order = Order.objects.create(
            created_by=self.user,
            product=self.product,
            total=99.99
        )
        self.assertEqual(order.created_by, self.user)
        self.assertEqual(order.total, 99.99)

# api/tests/test_views.py
from rest_framework.test import APITestCase
from rest_framework import status

class OrderAPITest(APITestCase):
    def setUp(self):
        # Test setup
        pass
    
    def test_create_order_authenticated(self):
        # Test order creation
        pass