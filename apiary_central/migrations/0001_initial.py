# Generated by Django 4.2.6 on 2023-10-30 08:28

import apiary_central.models
import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Apiary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('description', models.TextField(blank=True, null=True)),
                ('registration_number', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Apiary',
                'verbose_name_plural': 'Apiaries',
            },
        ),
        migrations.CreateModel(
            name='ApiaryHub',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(default=apiary_central.models.generate_api_key, max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=20)),
                ('end_date', models.DateField(default=datetime.date(2099, 12, 31))),
                ('last_connected_at', models.DateTimeField(blank=True, null=True)),
                ('battery_level', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('software_version', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('description', models.TextField(blank=True, null=True)),
                ('apiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hubs', to='apiary_central.apiary')),
            ],
        ),
        migrations.CreateModel(
            name='DataTransmission',
            fields=[
                ('transmission_uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transmission_tries', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1000.0)])),
                ('start_timestamp', models.DateTimeField()),
                ('end_timestamp', models.DateTimeField()),
                ('apiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transmissions', to='apiary_central.apiaryhub')),
            ],
        ),
        migrations.CreateModel(
            name='Hive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('apiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hives', to='apiary_central.apiary')),
            ],
        ),
        migrations.CreateModel(
            name='HiveComponentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_reading', models.FloatField(blank=True, null=True)),
                ('hive', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='apiary_central.hive')),
            ],
        ),
        migrations.CreateModel(
            name='SensorType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('value', models.FloatField()),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='apiary_central.sensor')),
                ('transmission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data', to='apiary_central.datatransmission')),
            ],
            options={
                'verbose_name': 'Sensor data',
                'verbose_name_plural': 'Sensor data',
            },
        ),
        migrations.AddField(
            model_name='sensor',
            name='sensor_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apiary_central.sensortype'),
        ),
        migrations.CreateModel(
            name='HiveComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('hive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='apiary_central.hive')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apiary_central.hivecomponenttype')),
            ],
        ),
    ]
