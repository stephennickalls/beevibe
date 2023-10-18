from django.shortcuts import render
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework import serializers
from .models import Apiary, Hive, Sensor, SensorData
from .serializers import ApiarySerializer, HiveSerializer, SensorSerializer, SensorDataSerializer, SensorDataUploadSerializer

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
    serializer_class = SensorDataUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, many=True)
        if serializer.is_valid():
            self.save_data(serializer.validated_data)
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def save_data(self, validated_data):
        for hive_data in validated_data:
            hive_id = hive_data['hive_id']
            timestamp = hive_data['timestamp']
            sensors = hive_data['sensors']
            for sensor_type, sensor_data in sensors.items():
                # logic to save each sensor reading goes here.
                # Find the hive using hive_id, find/create the sensor based on sensor_type,
                # and then save the sensor_data['value'] along with timestamp.
