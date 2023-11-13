from django.forms import ValidationError
from django.http import Http404
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
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Hive.objects.all()
        else:
            # Retrieve the apiary based on the URL parameter
            apiary_id = self.kwargs['apiary_pk']
            try:
                apiary = Apiary.objects.get(id=apiary_id, owner=user)
            except Apiary.DoesNotExist:
                raise Http404("No Apiary matches the given query.")
            return Hive.objects.filter(apiary=apiary)

    def get_serializer_context(self):
        return {'apiary_id': self.kwargs['apiary_pk']}
    
    
    def create(self, request, *args, **kwargs):
        user = request.user
        apiary_id = self.kwargs.get('apiary_pk')  # Corrected from 'api_key' to 'apiary_pk'
        if user.is_staff:
            return super().create(request, *args, **kwargs)

        # Check if the apiary belongs to the authenticated user
        if not Apiary.objects.filter(id=apiary_id, owner=user).exists():
            raise Http404("You do not have permission to add a Hive to this apiary.")

        # Proceed with the normal creation process
        modified_data = request.data.copy()
        modified_data.setdefault('apiary', apiary_id)
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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ApiaryHub.objects.all()
        else:
            # Filter based on ownership of the apiary
            return ApiaryHub.objects.filter(apiary__owner=user)

    def get_object(self):
        # Override the default behavior to use 'api_key' instead of 'pk'
        api_key = self.kwargs.get('api_key')
        user = self.request.user

        # Modify the query to ensure that the object belongs to the user's apiaries
        queryset = self.filter_queryset(self.get_queryset())

        try:
            obj = queryset.get(api_key=api_key)
        except ApiaryHub.DoesNotExist:
            raise PermissionDenied("You do not have an Apiary Hub with that api key")
        # No need to check object permissions here as the queryset already filters based on user
        return obj


    def create(self, request, *args, **kwargs):
        user = request.user
        apiary_id = request.data.get('apiary')
        if user.is_staff:
            return super().create(request, *args, **kwargs)
        # Check if the apiary belongs to the authenticated user
        if not Apiary.objects.filter(id=apiary_id, owner=user).exists():
            raise PermissionDenied("You do not have permission to add an ApiaryHub to this apiary.")
        # Proceed with the normal creation process
        return super().create(request, *args, **kwargs)

    
    
class SensorViewSet(ModelViewSet):
    # queryset = Sensor.objects.all().select_related('hive')
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Sensor.objects.all().select_related('hive')
        else:
            # Only return sensors that are in hives belonging to the user's apiaries
            return Sensor.objects.filter(hive__apiary__owner=user).select_related('hive')
    
    def create(self, request, *args, **kwargs):
        user = request.user
        hive_id = request.data.get('hive')

        # Check if the hive belongs to the current user
        if not Hive.objects.filter(id=hive_id, apiary__owner=user).exists():
            raise PermissionDenied("You do not have a hive set up with that id.")

        return super().create(request, *args, **kwargs)


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











