import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_basic_example():
    assert True

@pytest.mark.django_db
def test_health_check(api_client):
    response = api_client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}