from datetime import date
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count
from .utils import UUIDs



class Apiary(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])  # Accepts values from -90 to 90
    longitude = models.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])  # Accepts values from -180 to 180
    description = models.TextField(null=True, blank=True)
    registration_number = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apiaries')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Apiary"
        verbose_name_plural = "Apiaries"

class Hive(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    apiary = models.ForeignKey(Apiary, on_delete=models.CASCADE, related_name='hives')

    def __str__(self):
        return str(self.id)

class HiveComponentType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class HiveComponent(models.Model):
    hive = models.ForeignKey(Hive, on_delete=models.CASCADE, related_name="components")
    type = models.ForeignKey(HiveComponentType, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.type)
    

class TransmissionTimeSlot(models.Model):
    timeslot = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.timeslot)





class ApiaryHub(models.Model):
    api_key = models.UUIDField(unique=True, default=UUIDs.generate_api_key)
    config_sensors = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)
    end_date = models.DateField(default=date(2099, 12, 31))
    last_connected_at = models.DateTimeField(null=True, blank=True)
    battery_level = models.DecimalField(max_digits=4, decimal_places=2, 
                                        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], 
                                        null=True, blank=True)  # Values between 0-100 representing percentage
    software_version = models.DecimalField(max_digits=4, decimal_places=2, 
                                        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                                        null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timeslot = models.ForeignKey(TransmissionTimeSlot, on_delete=models.PROTECT)
    apiary = models.ForeignKey(Apiary, on_delete=models.CASCADE, related_name='hub')

    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new instance
            self.transmission_slot = self.get_least_populated_slot()
        super(ApiaryHub, self).save(*args, **kwargs)

    @staticmethod
    def get_least_populated_slot():
        slot_counts = TransmissionTimeSlot.objects.annotate(count=Count('apiaryhub')).order_by('count')
        if slot_counts.exists():
            return slot_counts.first()
        return None

    def __str__(self):
        return str(self.api_key)
    
class DataTransmission(models.Model):
    transmission_uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    apiary_hub = models.ForeignKey(ApiaryHub, on_delete=models.CASCADE, related_name='transmissions')
    transmission_tries = models.IntegerField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(1000.0)],)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField()
    
    def __str__(self):
        return str(self.transmission_uuid)
    
class SensorType(models.Model):
    TEMPERATURE_HUMIDITY = 'temp_hum'
    TEMPERATURE = 'temp'
    HUMIDITY = 'hum'
    WEIGHT = 'weight'

    SENSOR_TYPE_CHOICES = [
        (TEMPERATURE_HUMIDITY, 'Temperature and Humidity'),
        (TEMPERATURE, 'Temperature'),
        (HUMIDITY, 'Humidity'),
        (WEIGHT, 'Weight'),
    ]

    type = models.CharField(max_length=50, choices=SENSOR_TYPE_CHOICES, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.get_type_display()


class Sensor(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reading = models.DecimalField(max_digits=5, decimal_places=2, 
                                       validators=[MinValueValidator(0.0), MaxValueValidator(400.0)], null=True, blank=True)
    hive = models.ForeignKey(Hive, null=True, blank=True, on_delete=models.CASCADE, related_name='sensors')

    def __str__(self):
        return f"{str(self.uuid)} - {self.sensor_type}"


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    transmission = models.ForeignKey(DataTransmission, null=True, blank=True, on_delete=models.SET_NULL, related_name='data') # Link to the transmission
    timestamp = models.DateTimeField()
    value = models.FloatField()

    def __str__(self):
        return f"{self.value} at {self.timestamp} for {self.sensor.sensor_type}"
    
    class Meta:
        verbose_name = "Sensor data"
        verbose_name_plural = "Sensor data"


class DataTransmissionLog(models.Model):
    raw_data = models.JSONField()  # Storing raw JSON data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
