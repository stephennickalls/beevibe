from uuid import uuid4
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from apiary_central.models import Apiary, Hive, SensorType, Sensor, ApiaryHub, DataTransmission
from apiary_central.utils import UUIDs

User = get_user_model()

@pytest.mark.django_db
class TestDataTransmissionValidations(APITestCase):

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

        self.sensor_type_temp = SensorType.objects.create(
            type = 'temp',
            description = 'A temp sensor'
        )

        self.sensor1 = Sensor.objects.create(
            sensor_type = self.sensor_type_weight,
            last_reading = 98,
            hive = self.hive1 # belongs to user1
        )
        self.sensor2 = Sensor.objects.create(
            sensor_type = self.sensor_type_temp,
            last_reading = 98,
            hive = self.hive1 # belongs to user1
        )

        self.apiaryhub1 = ApiaryHub.objects.create(
            api_key = "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            created_at = "2023-10-18T02:45:00Z",
            type = 'esp32',
            end_date = '2023-12-31',
            last_connected_at = "2023-10-18T04:45:00Z",
            battery_level = 4.8,
            software_version = 1.1,
            description = 'A test description',
            apiary = self.apiary1
        )

        self.datatransmission1 = DataTransmission.objects.create(
            transmission_uuid = "a441d182-bd2a-460a-89bf-cc354b09a0fa",
            apiary_hub = self.apiaryhub1,
            transmission_tries = 2,
            start_timestamp = "2023-10-18T04:30:00Z",
            end_timestamp = "2023-10-18T04:45:00Z",
        )
  

    def test_data_transmission_with_valid_data_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": [
                {
                    "sensors": [
                        {
                            "sensor_id": str(self.sensor2.pk), 
                            "type": "TEMP",
                            "readings": [
                                {"timestamp": "2023-10-18T02:45:00Z", "value": 25.2},
                                {"timestamp": "2023-10-18T03:00:00Z", "value": 25.0}
                            ]
                        }
                    ]
                }
            
            ]
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED


    def test_data_transmission_with_in_valid_api_key_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "a441d192-bd2a-460a-89bf-cc354b09a0ff", # invalid key - api key not in the database so apiary hub cannot authenticate. Apiary hub must have a valid api key
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_with_duplicate_transmission_uuid_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0fa", # duplicate uuid 
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_with_neagative_transmission_tries_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff", 
            "transmission_tries": -2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_with_transmission_tries_greater_than_1000_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff", 
            "transmission_tries": 1001,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_with_transmission_tries_string_cast_to_decimal_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff", 
            "transmission_tries": "50",
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_data_transmission_with_invalid_start_time_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff", 
            "transmission_tries": 50,
            "start_timestamp": "2023-10-18",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_with_boolean_in_start_time_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff", 
            "transmission_tries": 50,
            "start_timestamp": True,
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_with_invalid_end_time_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_with_string_in_end_time_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "test",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_negative_software_version_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": -1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_software_version_greater_than_100_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 100.1,
            "battery": 4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_negative_battery_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": -4.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_batter_greater_than_100_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1,
            "battery": 104.8,
            "type": "esp32",
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_decimal_type_cast_to_string_returns_201(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1,
            "battery": 4.8,
            "type": 4.9,
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_data_transmission_boolean_in_type_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1,
            "battery": 4.8,
            "type": True,
            "data": []
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_data_transmission_with_sensor_uuid_that_does_not_exist_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": [
                {
                    "sensors": [
                        {
                            "sensor_id": str(UUIDs.generate_uuid()), 
                            "type": "TEMP",
                            "readings": [
                                {"timestamp": "2023-10-18T02:45:00Z", "value": 25.2},
                                {"timestamp": "2023-10-18T03:00:00Z", "value": 25.0}
                            ]
                        }
                    ]
                }
            
            ]
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    def test_data_transmission_readings_with_strinf_value_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": [
                {
                    "sensors": [
                        {
                            "sensor_id": str(self.sensor2.pk), 
                            "type": "TEMP",
                            "readings": '"timestamp": "2023-10-18T02:45:00Z", "value": 25.2'
                        }
                    ]
                }
            
            ]
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_data_transmission_invalid_reading_timestamp_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
            "transmission_tries": 2,
            "start_timestamp": "2023-10-18T02:45:00Z",
            "end_timestamp": "2023-10-18T04:45:00Z",
            "software_version": 1.1,
            "battery": 4.8,
            "type": "esp32",
            "data": [
                {
                    "sensors": [
                        {
                            "sensor_id": str(self.sensor2.pk), 
                            "type": "TEMP",
                            "readings": [
                                {"timestamp": "2023-10-18", "value": 25.2},
                                {"timestamp": "2023-10-18T03:00:00Z", "value": 25.0}
                            ]
                        }
                    ]
                }
            
            ]
        }
        response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # def test_data_transmission_invalid_reading_timestamp_returns_400(self):
    #     self.client.force_authenticate(user=self.user1)
    #     data = {
    #         "api_key": "d441d182-bd2a-460a-89bf-cc354b09a0ff",
    #         "transmission_uuid": "a441d182-bd2a-460a-89bf-cc354b09a0ff",
    #         "transmission_tries": 2,
    #         "start_timestamp": "2023-10-18T02:45:00Z",
    #         "end_timestamp": "2023-10-18T04:45:00Z",
    #         "software_version": 1.1,
    #         "battery": 4.8,
    #         "type": "esp32",
    #         "data": [
    #             {
    #                 "sensors": [
    #                     {
    #                         "sensor_id": str(self.sensor2.pk), 
    #                         "type": "TEMP",
    #                         "readings": [
    #                             {"timestamp": "2023-10-18T03:00:00Z", "value": 25.2},
    #                             {"timestamp": "2023-10-18T03:00:00Z", "value": 25.0}
    #                         ]
    #                     }
    #                 ]
    #             }
            
    #         ]
    #     }
    #     response = self.client.post(f'/api/datacollection/datatransmission/', data, format='json')
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST

    

