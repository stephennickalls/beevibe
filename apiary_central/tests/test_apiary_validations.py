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


    def test_apiary_creation_with_valid_data_returns_201(self):
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


    def test_apiary_creation_with_invalid_latitude_returns_400(self):
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

    def test_apiary_creation_with_invalid_longitude_returns_400(self):
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

    def test_apiary_creation_with_duplicate_registration_returns_400(self):
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


    def test_apiary_creation_without_required_owner_returns_400(self):
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

    def test_apiary_creation_without_required_registration_number_returns_400(self):
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

    def test_apiary_creation_without_required_latitude_returns_400(self):
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

    def test_apiary_creation_without_required_longitude_returns_400(self):
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

    def test_apiary_creation_with_invalid_data_type_in_description_field_is_cast_to_string(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name', 
            'latitude': 90.0,
            'longitude': 100.0,
            'description': True,
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['description'] == 'True'

    def test_apiary_creation_with_invalid_data_type_in_name_field_is_cast_to_string(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 100, 
            'latitude': 90.0,
            'longitude': 100.0,
            'description': 'A description',
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '100'

    
    def test_apiary_creation_with_invalid_data_type_in_latitude_field_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Best name ever', 
            'latitude': 'Test',
            'longitude': 100.0,
            'description': 'A description',
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_apiary_creation_with_invalid_data_type_in_longitude_field_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Best name ever', 
            'latitude': 80.00,
            'longitude': True,
            'description': 'A description',
            'registration_number': 'sd3356',
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_apiary_creation_with_invalid_data_type_in_registration_field_is_cast_to_string(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Best name ever', 
            'latitude': 80.00,
            'longitude': 50.00,
            'description': 'A description',
            'registration_number': False,
            'owner': self.user1.id
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['registration_number'] == 'False'


    def test_apiary_creation_with_invalid_data_type_in_owner_field_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'Best name ever', 
            'latitude': 80.00,
            'longitude': 50.00,
            'description': 'A description',
            'registration_number': False,
            'owner': True
            
        }
        response = self.client.post('/api/apiaries/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST