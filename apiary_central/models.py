from uuid import uuid4
from django.db import models
from django.conf import settings

class HiveComponent(models.Model):
    COMPONENT_CHOICES = (
        ('BROOD_BOX', 'Brood Box'),
        ('HONEY_SUPER_3_4', 'Honey super 3/4'),
        ('HONEY_SUPER_1_2', 'Honey super 1/2'),
        ('QUEEN_EXCLUDER', 'Queen excluder'),
        ('BASE', 'Base'),
        ('HIVE_MAT', 'Hive Mat'),
        ('LID', 'Lid'),
        ('FEEDER', 'Feeder'),
        ('OTHER', 'Other'),
    )
    type = models.CharField(max_length=16, choices=COMPONENT_CHOICES, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.type

class Apiary(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()  # Accepts values from -90 to 90
    longitude = models.FloatField()  # Accepts values from -180 to 180
    description = models.TextField(null=True, blank=True)
    registration_number = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apiaries')

    def __str__(self):
        return self.name

class Hive(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    apiary = models.ForeignKey(Apiary, on_delete=models.CASCADE, related_name='hives')
    components = models.ManyToManyField(HiveComponent, related_name='hives')

    def __str__(self):
        return self.name


class Sensor(models.Model):
    SENSOR_TYPES = (
        ('TEMP', 'Temperature'),
        ('WEIGHT', 'Weight'),
        ('HUMIDITY', 'Humidity'),
        ('AUDIO', 'Audio') 
    )
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    type = models.CharField(max_length=8, choices=SENSOR_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_reading = models.FloatField(null=True, blank=True)
    authentication_token = models.CharField(max_length=255, unique=True)
    token_last_refreshed = models.DateTimeField(auto_now_add=True)
    hive = models.ForeignKey(Hive, null=True, blank=True, on_delete=models.CASCADE, related_name='sensors')

    class Meta:
        unique_together = ('hive', 'type')

    def __str__(self):
        return f"{self.type} for {self.hive.name}"

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.value} at {self.timestamp} for {self.sensor.type}"