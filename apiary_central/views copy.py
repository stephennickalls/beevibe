from django.forms import ValidationError
from django.shortcuts import render
from django.db.models.aggregates import Count
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework import serializers
from .models import Apiary, Hive, Sensor, SensorData, DataTransmission, ApiaryHub
from .serializers import ApiarySerializer, HiveSerializer, SensorSerializer, SensorDataSerializer





class ApiaryViewSet(ModelViewSet):
    queryset = Apiary.objects.all()
    serializer_class = ApiarySerializer


class HiveViewSet(ModelViewSet):
    serializer_class = HiveSerializer

    def get_queryset(self):
        return Hive.objects.filter(apiary_id=self.kwargs['apiary_pk'])

    def get_serializer_context(self):
        return {'apiary_id': self.kwargs['apiary_pk']}
    
class SensorViewSet(ModelViewSet):
    queryset = Sensor.objects.all().select_related('hive')
    serializer_class = SensorSerializer

class SensorDataViewSet(ModelViewSet): # TODO : reduce this to POST and GET - we do not need update or delete here
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        return SensorData.objects.filter(sensor_id=self.kwargs['sensor_pk'])
    
    def get_serializer_context(self):
        return {'sensor_id': self.kwargs['sensor_pk']}


class SensorDataUploadViewSet(ModelViewSet):
    serializer_class = SensorDataSerializer
    queryset = SensorData.objects.all()

    @transaction.atomic
    def create(self, request, *args, **kwargs): 
        try:
        # get transmision and apiary hub data
            apiary_id = request.data.get("apiary_id")
            apiary_hub_uuid = request.data.get('apiary_hub').replace("-", "") # validated in model
            transmission_uuid = request.data.get('transmission_uuid').replace("-", "") # validated in model
            transmission_tries = request.data.get('transmission_tries') # validated in model
            start_timestamp = request.data.get('start_timestamp') # validated in model
            end_timestamp = request.data.get('end_timestamp') # validated in model
            software_version = request.data.get('softwear_version') # validated in model
            battery = request.data.get('battery') # validated in model
            type = request.data.get('type') # validated in model
            hub_status = request.data.get('hub_status') # validated in model

            # get hive and sensors data
            hive_data = request.data.get('data', [])

            # check apiary hub exists      
            apiary_hub = ApiaryHub.objects.get(uuid=apiary_hub_uuid)

        except ApiaryHub.DoesNotExist as e:
            return Response({"Apiary Hub not registered. Please register your Apiary Hub": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            # Create a DataTransmision instance and call save
        try:
            data_transmission_record = DataTransmission(
                apiary_uuid=apiary_hub,
                transmission_uuid=transmission_uuid,
                transmission_tries=transmission_tries,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )
            data_transmission_record.save()

            # save hive and sensor data
            for data in hive_data:
                sensors_data = data['sensors']
                for sensor_uuid, sensor_reading in sensors_data.items():
                    try:
                        sensor_uuid = sensor_uuid.replace("-", "")
                        sensor_id = Sensor.objects.get(uuid=sensor_uuid)
                        timestamp = sensor_reading['timestamp']
                        value = sensor_reading['value']
                        data_reading = SensorData(
                            sensor_id=sensor_id,
                            transmission=DataTransmission.objects.get(transmission_uuid=transmission_uuid.replace("-", "")),
                            timestamp=timestamp,
                            value=value
                        )
                        data_reading.save() # save sensor data
                    except Sensor.DoesNotExist as e:
                        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    except DataTransmission.DoesNotExist as e:
                        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

        
