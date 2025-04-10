import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.mark.django_db
class TestVegetarianAPI:
    def test_vegetarian_endpoint_requires_auth(self, api_client):
        """Test that the vegetarian endpoint requires authentication"""
        response = api_client.get('/api/vegetarian/')
        assert response.status_code == 401  # Unauthorized

    def test_vegetarian_endpoint_with_auth(self, api_client, test_user):
        """Test that authenticated users can access the vegetarian endpoint"""
        api_client.force_authenticate(user=test_user)
        response = api_client.get('/api/vegetarian/')
        assert response.status_code == 200
        assert 'vegetarian_users' in response.json()