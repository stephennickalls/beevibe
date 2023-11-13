import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apiary_central.models import Apiary, Hive, SensorType, Sensor

User = get_user_model()

@pytest.mark.django_db
class TestSensorPermissions(APITestCase):

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

        

    def test_if_user_is_authenticated_creating_sensor_returns_201(self):
        self.client.force_authenticate(user=self.user1) # authenticated
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 98,
            'hive':  self.hive1

        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_201_CREATED


    def test_if_user_is_anonymous_creating_sensor_returns_401(self):
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 98,
            'hive':  self.hive1

        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_sensor_creation_with_other_users_hive_returns_403(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 98,
            'hive':  self.hive2 # hive belongs to user2

        }
        response = self.client.post(f'/api/datacollection/sensors/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_user_can_access_own_sensors_returns_200(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/datacollection/sensors/')
        assert response.status_code == status.HTTP_200_OK
        count = 0
        for i in response.data:
            count = count+1
        assert count == 1

    def test_user_cannot_access_other_users_sensors_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        sensor_id = self.sensor2.uuid # belongs to user2
        response = self.client.get(f'/api/datacollection/sensors/{sensor_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND   
    
    def test_user_can_delete_own_sensor_returns_204(self):
        self.client.force_authenticate(user=self.user1)
        sensor_id = self.sensor1.uuid 
        response = self.client.delete(f'/api/datacollection/sensors/{sensor_id}/') 
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_cannot_delete_other_users_sensor_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        sensor_id = self.sensor2.uuid 
        response = self.client.delete(f'/api/datacollection/sensors/{sensor_id}/') 
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_sensor_returns_200(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 102,
            'hive':  self.hive1 

        }
        sensor_id = self.sensor1.uuid 
        response = self.client.patch(f'/api/datacollection/sensors/{sensor_id}/', data) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sensor1.refresh_from_db()
        assert self.sensor1.last_reading == 102

    def test_user_cannot_update_other_users_hive_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'sensor_type': self.sensor_type_weight.pk,
            'last_reading': 105,
            'hive':  self.hive2 # user2's hive
        }
        sensor_id = self.sensor2.uuid # user2's sensor
        response = self.client.patch(f'/api/datacollection/sensors/{sensor_id}/', data)
        assert response.status_code == status.HTTP_404_NOT_FOUND