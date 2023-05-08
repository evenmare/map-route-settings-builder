import pytest

from django.test import Client


api_client = Client()


def test_health_api():
    response = api_client.get('/api/v1/health')
    assert response.status_code == 200


# TODO: тестирование API
