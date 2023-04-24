import pytest

from django.test import Client


api_client = Client()


@pytest.mark.parametrize('url', ['/api/v1/health', '/api/v1/health/'])
def test_health_api(url):
    response = api_client.get(url)
    assert response.status_code == 200
