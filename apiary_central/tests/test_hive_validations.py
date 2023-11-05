import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from apiary_central.models import Apiary


User = get_user_model()

@pytest.mark.django_db
class TestHiveValidations(APITestCase):
     

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

    

    def test_hive_creation_with_valid_data(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 'test name',
            'description': "a great hive description",
            'apiary': self.apiary1.id
        }
        response = self.client.post(f'/api/apiaries/{self.apiary1.id}/hives/', valid_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_hive_creation_without_required_apiary(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'name': 'test name',
            'description': "a great description",
        }
        response = self.client.post(f'/api/apiaries/{self.apiary1.id}/hives/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_hive_creation_with_int_in_name_text_field(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 1,
            'description': "a great hive description",
            'apiary': self.apiary1.id
        }
        response = self.client.post(f'/api/apiaries/{self.apiary1.id}/hives/', valid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
