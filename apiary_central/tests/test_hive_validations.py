import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

@pytest.mark.django_db
class TestHiveValidations(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@email.com', password="test")
        self.user2 = User.objects.create_user(username='user2', email='user2@email.com', password="test")