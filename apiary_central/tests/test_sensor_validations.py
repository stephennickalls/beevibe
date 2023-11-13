from decimal import Decimal
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from apiary_central.models import Apiary, Hive, Sensor, SensorType


User = get_user_model()

@pytest.mark.django_db
class TestSensorValidations(APITestCase):
     

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@email.com', password="test")
        self.user2 = User.objects.create_user(username='user2', email='user2@email.com', password="test")
        self.staffuser = User.objects.create_user(username='staffuser', email='staffuser@email.com', password="test", is_staff=True)
        # Set one apiary with one hive
        self.apiary1 = Apiary.objects.create(
                name='Apiary1',
                latitude=38.0,
                longitude=118.0,
                registration_number='kb9989',
                owner=self.user1
        )
        self.hive1 = Hive.objects.create(
                name = 'Test Hive',
                description ='Test Hive Description',
                apiary = self.apiary1
        )
        # Set one apiary with one hive
        self.apiary2 = Apiary.objects.create(
                name='Apiary2',
                latitude=39.0,
                longitude=119.0,
                registration_number='kb9981',
                owner=self.user2
        )
        self.hive2 = Hive.objects.create(
                name = 'Test Hive',
                description ='Test Hive Description',
                apiary = self.apiary2
        )

        self.sensor_type_weight = SensorType.objects.create(
            type = 'weight',
            description = 'A weight sensor'
        )

        self.sensor1 = Sensor.objects.create(
            sensor_type = self.sensor_type_weight,
            last_reading = 98,
            hive = self.hive1 # belongs to user1
        )
        self.sensor2 = Sensor.objects.create(
            sensor_type = self.sensor_type_weight,
            last_reading = 98,
            hive = self.hive2 # belongs to user2
        )

    

    def test_sensor_creation_with_valid_data__returns_201(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 98,
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_sensor_creation_with_invalid_data_type_in_sensor_type_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': True,
            'last_reading': 98,
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sensor_creation_with_invalid_data_type_in_last_reading_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': True,
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sensor_creation_with_string_decimal_cast_to_decimal_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': '102',
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['last_reading'] == Decimal('102')

    def test_sensor_creation_with_negative_last_reading_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': -1,
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sensor_creation_with_last_reading_greater_than_500_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 501,
            'hive':  self.hive1
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_sensor_creation_with_hive_that_does_not_exist_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': -1,
            'hive':  7
        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
