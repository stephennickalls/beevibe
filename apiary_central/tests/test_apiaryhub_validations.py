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









# TODO: Data Integrity on Update: Ensure that updates to an ApiaryHub do not unintentionally alter unrelated fields or related objects.