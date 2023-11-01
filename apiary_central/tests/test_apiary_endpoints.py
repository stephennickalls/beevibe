import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apiary_central.models import Apiary

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='user', password='test')

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
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


    def test_if_user_is_anonymous_returns_401(self):
        api_client = APIClient() # NOT authenticated
        data = {
            'name': 'Test Apiary',
            'latitude': -38.80895,
            'longitude': 118.35449,
            'description': 'Test Description',
            'registration_number': 'kb99887',
        }
        response = api_client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

class ApiaryPermissionTests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@email.com', password="test")
        self.user2 = User.objects.create_user(username='user2', email='user2@email.com', password="test")

        self.apiary1 = Apiary.objects.create(
                name='Apiary1',
                latitude=38.0,
                longitude=118.0,
                registration_number='kb9989',
                owner=self.user1
        )
        self.apiary2 = Apiary.objects.create(
                name='Apiary1',
                latitude=39.0,
                longitude=119.0,
                registration_number='kb9981',
                owner=self.user2
        )

    def test_user_can_access_own_apiary(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/apiaries/{self.apiary1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.apiary1.name)