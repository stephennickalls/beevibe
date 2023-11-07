import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from apiary_central.models import Apiary, ApiaryHub
from apiary_central.utils import FormatUUIDs


User = get_user_model()

@pytest.mark.django_db
class TestApiaryHubPermissions(APITestCase):   

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@email.com', password="test")
        self.user2 = User.objects.create_user(username='user2', email='user2@email.com', password="test")
        self.staffuser = User.objects.create_user(username='staffuser', email='staffuser@email.com', password="test", is_staff=True)

        self.apiary1 = Apiary.objects.create(
                name='Apiary1',
                latitude=38.0,
                longitude=118.0,
                registration_number='kb9989',
                owner=self.user1
        )

        self.apiary2 = Apiary.objects.create(
                name='Apiary2',
                latitude=40.0,
                longitude=120.0,
                registration_number='hg9989',
                owner=self.user2
        )
        self.apiary3 = Apiary.objects.create(
                name='Apiary3',
                latitude=41.0,
                longitude=120.0,
                registration_number='ui9989',
                owner=self.staffuser
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

        self.apiaryhub2 = ApiaryHub.objects.create(
            type = 'esp32',
            end_date = '2023-12-20',
            last_connected_at = '2023-11-06T15:30:00.123456',
            battery_level = 4.8,
            software_version = 1.10,
            description = 'Great description of apiary hub 2',
            apiary = self.apiary2
        )
        self.apiaryhub3 = ApiaryHub.objects.create(
            type = 'esp32',
            end_date = '2023-12-19',
            last_connected_at = '2023-11-06T15:30:00.123456',
            battery_level = 4.9,
            software_version = 1.00,
            description = 'Great description of apiary hub 3',
            apiary = self.apiary3
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

    def test_apiaryhub_creation_with_other_users_apiary_returns_403(self):
        print("Test started")
        self.client.force_authenticate(user=self.user1)
        data = {
            'type': 'esp32',
            'end_date': '2023-12-31',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level': 4.7,
            'software_version': 1.11,
            'description': 'Great description',
            'apiary': self.apiary2.pk # apiary2 belongs to user2
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_user_can_access_own_apiaryhub_returns_200(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/datacollection/apiaryhubs/')
        first_response_item = response.data[0]
        api_key = first_response_item['api_key']
        assert response.status_code == status.HTTP_200_OK
        assert api_key.replace('-', '') == self.apiaryhub1.api_key # check api keys without -'s match

    def test_user_cannot_access_other_users_apiaryhubs_returns_403(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/datacollection/apiaryhubs/{FormatUUIDs.add_hyphens_to_uuid(self.apiaryhub2.api_key)}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_staff_user_can_delete_own_apiaryhub_returns_204(self):
        self.client.force_authenticate(user=self.staffuser)
        api_key = FormatUUIDs.add_hyphens_to_uuid(self.apiaryhub3.api_key)
        response = self.client.delete(f'/api/datacollection/apiaryhubs/{api_key}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Check if the hive has been deleted
        self.assertFalse(ApiaryHub.objects.filter(api_key=api_key).exists())

    def test_staff_user_can_delete_other_users_apiaryhub_returns_204(self):
        self.client.force_authenticate(user=self.staffuser)
        api_key = FormatUUIDs.add_hyphens_to_uuid(self.apiaryhub2.api_key)
        response = self.client.delete(f'/api/datacollection/apiaryhubs/{api_key}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Check if the hive has been deleted
        self.assertFalse(ApiaryHub.objects.filter(api_key=api_key).exists())

    def test_user_can_delete_own_apiaryhub_returns_204(self):
        self.client.force_authenticate(user=self.user1)
        api_key = FormatUUIDs.add_hyphens_to_uuid(self.apiaryhub1.api_key)
        response = self.client.delete(f'/api/datacollection/apiaryhubs/{api_key}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Check if the hive has been deleted
        self.assertFalse(ApiaryHub.objects.filter(api_key=api_key).exists())
    
    # def test_user_cannot_delete_other_users_hive_returns_403(self):
    #     self.client.force_authenticate(user=self.user2)
    #     response = self.client.delete(f'/api/apiaries/{self.apiary1.id}/hives/{self.hive1.id}/')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_user_can_only_see_own_hives_in_list_returns_200(self):
    #     self.client.force_authenticate(user=self.user1)
    #     response = self.client.get(f'/api/apiaries/{self.apiary1.id}/hives/')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     # Assuming the response.data is a list of hives
    #     # Check that each hive belongs to an apiary owned by user1
    #     for hive in response.data:
    #         # Fetch the apiary for each hive to check its owner
    #         apiary = Apiary.objects.get(id=hive['apiary'])
    #         assert apiary.owner.id == self.user1.id

    # def test_user_can_update_own_hive_returns_200(self):
    #     self.client.force_authenticate(user=self.user1)
    #     updated_data = {
    #         'name': "Updated Hive",
    #         'description': 'Updated Hive Description'
    #     }
    #     response = self.client.patch(f'/api/apiaries/{self.apiary1.id}/hives/{self.hive1.id}/', updated_data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.hive1.refresh_from_db()
    #     assert self.hive1.name == 'Updated Hive'

    # def test_user_cannot_update_other_users_hive_returns_403(self):
    #     self.client.force_authenticate(user=self.user1)
    #     update_data = {'name': 'Should Not Update'}
    #     response = self.client.patch(f'/api/apiaries/{self.apiary2.id}/hives/{self.hive2.id}/', update_data)
    #     assert response.status_code == status.HTTP_403_FORBIDDEN
