import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='user', password='test')

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

class TestCreateApiary:
    def test_if_user_is_authenticated_returns_201(self, api_client, user):
        data = {
            'name': 'Test Apiary',
            'latitude': -38.80895,
            'longitude': 118.35449,
            'description': 'Test Description',
            'registration_number': 'kb99887',
            'owner': user.id
        }
        response = api_client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Apiary'
        assert response.data['owner'] == user.id  # Make sure the owner is set correctly
