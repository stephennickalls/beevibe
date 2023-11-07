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

    def test_apiaryhub_creation_with_valid_data_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        valid_data = {
            'type': 'test hub name',
            'end_date': '2023-12-19',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level': 3.5,
            'software_version': 1.20,
            'description': 'Test hub description',
            'apiary': self.apiary1.id # apiary owned by user1
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', valid_data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_apiarycreation_creation_with_invalid_enddate_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'type': 'test hub name',
            'end_date': '2023-12-42', # invalid date
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level ': 3.5,
            'software_version': 1.20,
            'description': 'Test hub description',
            'apiary': self.apiary1.id # apiary owned by user1
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiaryhub_creation_with_invalid_last_connected_at_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'type': 'test hub name',
            'end_date': '2023-12-20',
            'last_connected_at': '2023-11-06', # invalid date time
            'battery_level ': 3.5,
            'software_version': 1.20,
            'description': 'Test hub description',
            'apiary': self.apiary1.id # apiary owned by user1
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apiaryhub_creation_with_negative_battery_level__returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'type': 'test hub name',
            'end_date': '2023-12-42',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level ': -3.5,
            'software_version': 1.20,
            'description': 'Test hub description',
            'apiary': self.apiary1.id # apiary owned by user1
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
     

    def test_apiaryhub_creation_with_battery_level_greater_than_100__returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'type': 'test hub name',
            'end_date': '2023-12-42',
            'last_connected_at': '2023-11-06T15:30:00.123456',
            'battery_level ': 101,
            'software_version': 1.20,
            'description': 'Test hub description',
            'apiary': self.apiary1.id # apiary owned by user1
        }
        response = self.client.post('/api/datacollection/apiaryhubs/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_apiary_creation_without_required_owner_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'test name',
    #         'latitude': 90.0, 
    #         'longitude': 100.0,
    #         'description': "a great description",
    #         'registration_number': 'gh9984',
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_apiary_creation_without_required_registration_number_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'test name',
    #         'latitude': 90.0, 
    #         'longitude': 100.0,
    #         'description': "a great description",
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_apiary_creation_without_required_latitude_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'test name', 
    #         'longitude': 100.0,
    #         'description': "a great description",
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_apiary_creation_without_required_longitude_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'test name', 
    #         'latitude': 90.0,
    #         'description': "a great description",
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_apiary_creation_with_invalid_data_type_in_description_field_is_cast_to_string(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'test name', 
    #         'latitude': 90.0,
    #         'longitude': 100.0,
    #         'description': True,
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.data['description'] == 'True'

    # def test_apiary_creation_with_invalid_data_type_in_name_field_is_cast_to_string(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 100, 
    #         'latitude': 90.0,
    #         'longitude': 100.0,
    #         'description': 'A description',
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.data['name'] == '100'

    
    # def test_apiary_creation_with_invalid_data_type_in_latitude_field_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'Best name ever', 
    #         'latitude': 'Test',
    #         'longitude': 100.0,
    #         'description': 'A description',
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST


    # def test_apiary_creation_with_invalid_data_type_in_longitude_field_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'Best name ever', 
    #         'latitude': 80.00,
    #         'longitude': True,
    #         'description': 'A description',
    #         'registration_number': 'sd3356',
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST


    # def test_apiary_creation_with_invalid_data_type_in_registration_field_is_cast_to_string(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'Best name ever', 
    #         'latitude': 80.00,
    #         'longitude': 50.00,
    #         'description': 'A description',
    #         'registration_number': False,
    #         'owner': self.user1.id
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_201_CREATED
    #     assert response.data['registration_number'] == 'False'


    # def test_apiary_creation_with_invalid_data_type_in_owner_field_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         'name': 'Best name ever', 
    #         'latitude': 80.00,
    #         'longitude': 50.00,
    #         'description': 'A description',
    #         'registration_number': False,
    #         'owner': True
            
    #     }
    #     response = self.client.post('/api/apiaries/', data)
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST







# TODO: Data Integrity on Update: Ensure that updates to an ApiaryHub do not unintentionally alter unrelated fields or related objects.