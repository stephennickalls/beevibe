from django.forms import ValidationError
from django.shortcuts import render
from django.db.models.aggregates import Count
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

    def create(self, request, *args, **kwargs): 
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
        # data_entries = request.data.get('data', [])

        # check apiary hub exists
        try: 
            # check record exists
            
            apiary_hub = ApiaryHub.objects.get(uuid=apiary_hub_uuid)
        except ApiaryHub.DoesNotExist as e:
            return Response({"Apiary Hub not registered. Please register your Apiary Hub": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:  
            # Create a DataTransmision instance and call save
            data_transmission = DataTransmission(
                apiary_uuid=apiary_hub,
                transmission_uuid=transmission_uuid,
                transmission_tries=transmission_tries,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
            )
            data_transmission.save()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        return Response({"status": "success"}, status=status.HTTP_201_CREATED)


        # serializer = self.get_serializer(data=request.data, many=True)
        # if serializer.is_valid():
        #     self.save_data(serializer.validated_data)
        #     return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_transmission_data(self, raw_data):
        print(raw_data)

    def save_data(self, validated_data):
        for sensor_data in validated_data:
            hive_id = sensor_data['hive_id']
            timestamp = sensor_data['timestamp']
            print(f'hive id: {hive_id}, Timestamp: {timestamp}')
            sensors = sensor_data['sensors']
            for sensor_type, sensor_data in sensors.items():
                print(f'sensor type: {sensor_type}, sensor data: {sensor_data}')
                # logic to save each sensor reading goes here.
                # Find the hive using hive_id, find/create the sensor based on sensor_type,
                # and then save the sensor_data['value'] along with timestamp.
