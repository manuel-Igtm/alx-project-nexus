"""
conftest.py - Pytest fixtures for Project Nexus tests.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def create_user():
    """Factory fixture to create users."""
    def _create_user(email='test@example.com', password='testpass123', **kwargs):
        return User.objects.create_user(email=email, password=password, **kwargs)
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_user(create_user):
    """Create an admin user."""
    user = create_user(email='admin@example.com')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated admin API client."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
