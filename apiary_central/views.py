from django.forms import ValidationError
from django.shortcuts import render
from django.db.models.aggregates import Count
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import status
from rest_framework import serializers
from .models import Apiary, Hive, Sensor, SensorData, DataTransmission, ApiaryHub
from .permissions import IsHiveOwner, IsApiaryOwner
from .serializers import ApiarySerializer, HiveSerializer, SensorSerializer, SensorDataSerializer, DataTransmissionSerializer, ApiaryHubSerializer


class ApiaryViewSet(ModelViewSet):
    serializer_class = ApiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Apiary.objects.filter(owner=user)
    
    def create(self, request, *args, **kwargs):
        try:
            return super(ApiaryViewSet, self).create(request, *args, **kwargs)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HiveViewSet(ModelViewSet):
    serializer_class = HiveSerializer
    permission_classes = [IsAuthenticated, IsHiveOwner]

    def get_queryset(self):
        # Get the apiary based on the URL parameter and ensure it belongs to the current user
        user = self.request.user
        apiary = get_object_or_404(Apiary, id=self.kwargs['apiary_pk'], owner=user)
        # Return hives that belong to the retrieved apiary
        return Hive.objects.filter(apiary=apiary)

    def get_serializer_context(self):
        return {'apiary_id': self.kwargs['apiary_pk']}
    
    def create(self, request, *args, **kwargs):
        modified_data = request.data.copy()
        modified_data.setdefault('apiary', self.kwargs['apiary_pk'])
        serializer = self.get_serializer(data=modified_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class DataCollectionViewSet(ViewSet):
    """
    A ViewSet that represents the 'datacollection' endpoint.
    """

    def list(self, request):
        return Response({
            "message": "This is the Data Collection endpoint.",
            "endpoints": {
                "apiayhubdataupload": "/datacollection/apiaryhubs/apiayhubdataupload/",
                "apiaryhubs": "/datacollection/apiaryhubs/",
                "sensors": "/datacollection/sensors/"
            }
        })

class ApiaryHubViewSet(ModelViewSet):
    serializer_class = ApiaryHubSerializer
    permission_classes = [IsAuthenticated, IsApiaryOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ApiaryHub.objects.all()
        return ApiaryHub.objects.filter(apiary__owner=user)
    
    def get_object(self):
        # Override the default behavior to use 'api_key' instead of 'pk'
        api_key = self.kwargs.get('api_key')
        obj = get_object_or_404(ApiaryHub, api_key=api_key)
        result = self.check_object_permissions(self.request, obj)  # This enforces object-level permissions
        return obj
    
    
class SensorViewSet(ModelViewSet):
    queryset = Sensor.objects.all().select_related('hive')
    serializer_class = SensorSerializer

class SensorDataViewSet(ModelViewSet): # TODO : reduce this to POST and GET - we do not need update or delete here
    serializer_class = SensorDataSerializer

    def get_queryset(self):
        return SensorData.objects.filter(sensor_id=self.kwargs['sensor_pk'])
    
    def get_serializer_context(self):
        return {'sensor_id': self.kwargs['sensor_pk']}


class ApiaryHubDataUploadViewSet(ModelViewSet):
    serializer_class = SensorDataSerializer
    queryset = SensorData.objects.all()
    

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = DataTransmissionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # check hub is in the database using the api_key
                apiary_hub = self.get_apiary_hub(serializer.validated_data['api_key'])
                data_transmission_record = self.create_data_transmission_record(serializer.validated_data, apiary_hub)
                self.create_sensor_data(serializer.validated_data['data'], data_transmission_record)
                return Response({"success": "Data created successfully"}, status=status.HTTP_201_CREATED)
            except (ApiaryHub.DoesNotExist, Sensor.DoesNotExist, ValidationError, IntegrityError) as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"unexpected_error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_apiary_hub(self, api_key):
        return ApiaryHub.objects.get(api_key=api_key)

    def create_data_transmission_record(self, validated_data, apiary_hub):
        data_transmission_record = DataTransmission(
                    transmission_uuid = validated_data['transmission_uuid'],
                    apiary=apiary_hub,
                    transmission_tries = validated_data['transmission_tries'],
                    start_timestamp = validated_data['start_timestamp'],
                    end_timestamp = validated_data['end_timestamp']
                )
        return data_transmission_record.save()

    def create_sensor_data(self, sensor_data, data_transmission_record):
        for hive_data in sensor_data:
            hive_id = hive_data['hive_id']
            for sensor_data in hive_data['sensors']:
                sensor = Sensor.objects.get(uuid=sensor_data['sensor_id']),
                for readings in sensor_data['readings']:
                    sensor_data_record = SensorData(
                        sensor = sensor[0],
                        transmission = data_transmission_record,
                        timestamp = readings['timestamp'],
                        value = readings['value']
                    )

                    sensor_data_record.save()











