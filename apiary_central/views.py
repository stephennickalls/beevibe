from django.forms import ValidationError
from django.shortcuts import render
from django.db.models.aggregates import Count
from django.db import transaction, IntegrityError
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
        response_data = {}
        response_status = status.HTTP_201_CREATED

        try:
  
            
            # get transmision and apiary hub data
            apiary_hub_uuid = request.data.get('apiary_hub').replace("-", "") # validated in model
            transmission_uuid = request.data.get('transmission_uuid').replace("-", "") # validated in model
            transmission_tries = request.data.get('transmission_tries') # validated in model
            start_timestamp = request.data.get('start_timestamp') # validated in model
            end_timestamp = request.data.get('end_timestamp') # validated in model
            # If apiary_hub does not exist
            apiary_hub = ApiaryHub.objects.get(uuid=apiary_hub_uuid)
            # get hive and sensors data
            hive_data = request.data.get('data', [])
            # if no error at this point we can go ahead and save the data transmission  
            print("before data transmission")          
            data_transmission_record = DataTransmission(
                    apiary_uuid=apiary_hub,
                    transmission_uuid=transmission_uuid,
                    transmission_tries=transmission_tries,
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                )
            data_transmission_record.save()
            print("after data transmission")  
            # save sensor data
            for data in hive_data:
                print("in data loop")
                sensors_data = data['sensors']
                for sensor_uuid, sensor_reading in sensors_data.items():
                    sensor_uuid = sensor_uuid.replace("-", "")
                    print(f'Sensor id = {sensor_uuid}')
                    sensor_id = Sensor.objects.get(uuid=sensor_uuid)
                    timestamp = sensor_reading['timestamp']
                    print("after Sensor")
                    value = sensor_reading['value']

                    transmission = DataTransmission.objects.get(transmission_uuid=transmission_uuid)
                    print("###")
                    print(f'Sensor id = {sensor_uuid}')
                    print(f'transmission {transmission.replace("-", "")}')
                    print(f'timestamp {timestamp}')
                    print(f'value {value}')
                    print("###")
                    # data_reading = SensorData(
                    #     sensor_id=sensor_id,
                    #     transmission=transmission_uuid,
                    #     timestamp=timestamp,
                    #     value=value
                    # )

                    # print("after creating data_reading object")
                    # data_reading.save() # save sensor data
        except ApiaryHub.DoesNotExist:
            response_data = {"Error": "Data transmission not found"}
            response_status = status.HTTP_400_BAD_REQUEST
        except DataTransmission.DoesNotExist:
            response_data = {"Error": "Data transmission not found"}
            response_status = status.HTTP_400_BAD_REQUEST
        except Sensor.DoesNotExist:
            response_data = {"Error": "Sensor not found"}
            response_status = status.HTTP_400_BAD_REQUEST 
        except ValidationError as e:
            response_data = {"VError": str(e)}
            response_status = status.HTTP_400_BAD_REQUEST
        except IntegrityError as e:
            response_data = {"IError": str(e)}
            response_status = status.HTTP_400_BAD_REQUEST
        except Exception as e:  # Catch all other exceptions
            response_data = {"error": "An unexpected error occurred. Please try again."}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response_data, status=response_status)









