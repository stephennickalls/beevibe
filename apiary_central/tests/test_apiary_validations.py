import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase


User = get_user_model()

@pytest.mark.django_db
class TestAliaryValidations(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@email.com', password="test")
        self.user2 = User.objects.create_user(username='user2', email='user2@email.com', password="test")


    def test_apiary_creation_with_valid_data(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 'test name',
            'latitude': 45.0,
            'longitude': 90.0,
            'description': "a great description",
            'registration_number': 'gh9984',
            'owner': self.user1.id
        }
        response = self.client.post('/api/apiaries/', valid_data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_apiary_creation_with_invalid_latitude(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 'test name',
            'latitude': 100.00, # invalid lat
            'longitude': 90.0,
            'description': "a great description",
            'registration_number': 'gh9984',
            'owner': self.user1.id
        }
        response = self.client.post('/api/apiaries/', valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiary_creation_with_invalid_longitude(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 'test name',
            'latitude': 90.0, 
            'longitude': 200.0, # invalid long
            'description': "a great description",
            'registration_number': 'gh9984',
            'owner': self.user1.id
        }
        response = self.client.post('/api/apiaries/', valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiary_creation_with_duplicate_registration(self):
        self.client.force_authenticate(user=self.user1)
        apiary_with_unique_registration = {
            'name': 'test name 1',
            'latitude': 90.0, 
            'longitude': 100.0, 
            'description': "a great description",
            'registration_number': 'gh9984',
            'owner': self.user1.id
        }
        self.client.post('/api/apiaries/', apiary_with_unique_registration)

        apiary_with_duplicate_registration = {
            'name': 'test name 2',
            'latitude': 56.0, 
            'longitude': 155.0, 
            'description': "a great description",
            'registration_number': 'gh9984',
            'owner': self.user1.id
        }
        response = self.client.post('/api/apiaries/', apiary_with_duplicate_registration)
        assert response.status_code == status.HTTP_400_BAD_REQUEST        


    def test_apiary_creation_without_required_owner(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name',
            'latitude': 90.0, 
            'longitude': 100.0,
            'description': "a great description",
            'registration_number': 'gh9984',
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiary_creation_without_required_registration_number(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name',
            'latitude': 90.0, 
            'longitude': 100.0,
            'description': "a great description",
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiary_creation_without_required_latitude(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name', 
            'longitude': 100.0,
            'description': "a great description",
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiary_creation_without_required_longitude(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name', 
            'latitude': 90.0,
            'description': "a great description",
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST