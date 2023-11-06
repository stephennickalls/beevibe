import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from apiary_central.models import Apiary, ApiaryHub


User = get_user_model()

@pytest.mark.django_db
class TestApiaryHubPermissions(APITestCase):
     

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

        self.apiaryhub1 = ApiaryHub.objects.create(
            type = 'esp32',
            end_date = '2023-12-31',
            last_connected_at = '2023-11-06T15:30:00.123456',
            battery_level = 4.7,
            software_version = 1.11,
            description = 'Great description',
            apiary = self.apiary1
        )

    def test_if_user_is_authenticated_creating_apiaryhub_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'type': 'esp32',
            'end_date': '2023-12-31',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level': 4.7,
            'software_version': 1.11,
            'description': 'Great description',
            'apiary': self.apiary1.pk
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', valid_data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_if_user_is_anonymous_creating_apiary_returns_401(self):
        data = {
            'type': 'esp32',
            'end_date': '2023-12-31',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level': 4.7,
            'software_version': 1.11,
            'description': 'Great description',
            'apiary': self.apiary1.pk
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
