import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apiary_central.models import Apiary

User = get_user_model()

@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
class TestApiaryBehaviour(APITestCase):

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

    def test_if_user_is_authenticated_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'name': 'Test Apiary',
            'latitude': -38.80895,
            'longitude': 118.35449,
            'description': 'Test Description',
            'registration_number': 'kb99887',
            'owner': self.user1.id
        }
        response = self.client.post('/api/apiaries/', valid_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Test Apiary'
        assert response.data['owner'] == self.user1.id  # Make sure the owner is set correctly


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


    def test_user_can_access_own_apiaries(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/apiaries/{self.apiary1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.apiary1.name)

    def test_user_cannot_access_other_users_apiaries(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/apiaries/{self.apiary2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_apiary(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/apiaries/{self.apiary1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Check if the apiary has been deleted
        self.assertFalse(Apiary.objects.filter(id=self.apiary1.id).exists())

    def test_user_cannot_delete_other_users_apiary(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/apiraries/{self.apiary2.id}')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_only_see_own_apiaries_in_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/apiaries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming the response data is a list of apiaries
        self.assertTrue(all(apiary['owner'] == self.user1.id for apiary in response.data))

    def test_user_can_update_own_apiary(self):
        self.client.force_authenticate(user=self.user1)
        update_data = {
            'name': "Updated Apiary",
            'description': 'Updated Description'
        }
        response = self.client.patch(f'/api/apiaries/{self.apiary1.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.apiary1.refresh_from_db()
        self.assertEqual(self.apiary1.name, 'Updated Apiary')

    def test_user_cannot_update_other_users_apiary(self):
        self.client.force_authenticate(user=self.user1)
        update_data = {'name': 'Should Not Update'}
        response = self.client.patch(f'/api/apiaries/{self.apiary2.id}/', update_data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

