from datetime import date
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
    
from django.db import models
from django.conf import settings

class ApiaryHub(models.Model):
    # UUID or Serial Number
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20)
    end_date = models.DateField(default=date(2099, 12, 31))
    STATUS_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('LOW_BATTERY', 'Low Battery'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OFFLINE')
    last_connected_at = models.DateTimeField(null=True, blank=True)
    battery_level = models.PositiveIntegerField(null=True, blank=True)  # Values between 0-100 representing percentage
    software_version = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    apiary = models.ForeignKey('Apiary', on_delete=models.CASCADE, related_name='hubs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hubs')

    def __str__(self):
        return str(self.uuid)



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
    token_last_refreshed = models.DateTimeField()
    hive = models.ForeignKey(Hive, null=True, blank=True, on_delete=models.CASCADE, related_name='sensors')

    class Meta:
        unique_together = ('hive', 'type')

    def __str__(self):
        return f"{self.type} for {self.hive.name}"

class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField()
    value = models.FloatField()

    def __str__(self):
        return f"{self.value} at {self.timestamp} for {self.sensor.type}"