from decimal import Decimal
from .models import Apiary, Hive, HiveComponent, Sensor, SensorData, HiveComponentType, ApiaryHub, DataTransmissionLog
from rest_framework import serializers
from .validators import validate_datetime_format




class ApiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Apiary
        fields = ['id', 'name', 'latitude', 'longitude', 'description', 'registration_number', 'owner']


class HiveComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiveComponent
        fields = ['type']


class HiveSerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField(method_name='get_components')

    component_types = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Hive
        fields = ['id', 'name', 'description', 'components', 'component_types', 'apiary']

    #### REMEMBER!!! when sending an object to the server you must use "component_types"!!!!!
    
    def get_components(self, obj):
        return [component.type for component in obj.components.all()]
    
    def create(self, validated_data):
        component_types = validated_data.pop('component_types', [])
        apiary_id = self.context['apiary_id']
        # print(f'apiary id =  {apiary_id}')
        hive = Hive.objects.create(apiary_id=apiary_id, **validated_data)
        
        for component_type in component_types:
            try:
                component = HiveComponent.objects.get(type=component_type)
                hive.components.add(component)
            except HiveComponent.DoesNotExist:
                raise serializers.ValidationError(f"Invalid component type: {component_type}")
                    
        return hive

def update(self, instance, validated_data):
    component_types = validated_data.pop('component_types', [])

    # Update other fields
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()

    # Delete the existing components for the hive
    HiveComponent.objects.filter(hive=instance).delete()

    # Add the new components based on their textual representation
    for component_type in component_types:
        try:
            component_type_instance = HiveComponentType.objects.get(name=component_type)
            HiveComponent.objects.create(hive=instance, type=component_type_instance)
        except HiveComponentType.DoesNotExist:
            raise serializers.ValidationError(f"Invalid component type: {component_type}")

    return instance

class ApiaryHubSerializer(serializers.ModelSerializer):
    api_key = serializers.UUIDField(read_only=True)
    apiary = serializers.PrimaryKeyRelatedField(queryset=Apiary.objects.all())
    last_connected_at = serializers.DateTimeField(validators=[validate_datetime_format])
    class Meta:
        model = ApiaryHub
        fields = ['api_key', 'type', 'end_date', 'last_connected_at', 'battery_level', 'software_version', 'description', 'apiary']

class SensorSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    hive = serializers.PrimaryKeyRelatedField(queryset=Hive.objects.all(), required=False, allow_null=True)
    last_reading = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=0.0,  # Minimum value
        max_value=400.0  # Maximum value
    )

    class Meta:
        model = Sensor
        fields = ['uuid', 'sensor_type', 'created_at', 'last_reading', 'hive']


class SensorDataSerializer(serializers.ModelSerializer):
    sensor = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = SensorData
        fields = ['sensor', 'timestamp', 'value']

    def create(self, validated_data):
        sensor_id = self.context['sensor_id']
        print(f'sensor id =  {sensor_id}')
        sensordata = SensorData.objects.create(sensor_id=sensor_id, **validated_data)
        return sensordata
    
class ReadingsSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField(validators=[validate_datetime_format])
    value = serializers.DecimalField(max_digits=5,decimal_places=2, max_value=99.99, min_value=0.00)
    
class SensorDataTransmissionSerializer(serializers.Serializer):
    sensor_id = serializers.UUIDField(format='hex')
    type = serializers.CharField(max_length=100)
    readings = ReadingsSerializer(many=True) 

class TransmissionDataSerializer(serializers.Serializer):
    sensors = SensorDataTransmissionSerializer(many=True)

class DataTransmissionSerializer(serializers.Serializer):
    api_key = serializers.UUIDField(format='hex')
    transmission_uuid = serializers.UUIDField(format='hex')
    transmission_tries = serializers.IntegerField(min_value=0, max_value=1000)
    start_timestamp = serializers.DateTimeField(validators=[validate_datetime_format])
    end_timestamp = serializers.DateTimeField(validators=[validate_datetime_format])
    software_version = serializers.DecimalField(max_digits=5,decimal_places=2, max_value=99.99, min_value=0.00)
    battery = serializers.DecimalField(max_digits=5, decimal_places=2, max_value=99.99, min_value=0.00)
    type = serializers.CharField(max_length=50)
    data = TransmissionDataSerializer(many=True)


class DataTransmissionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTransmissionLog
        fields = ['raw_data', 'create_at']

 



