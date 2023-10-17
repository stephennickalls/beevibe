# Generated by Django 4.2.6 on 2023-10-11 18:23

from django.db import migrations, models
import django.db.models.deletion


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
            name='HiveComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('BROOD_BOX', 'Brood Box'), ('HONEY_SUPER_3_4', 'Honey super 3/4'), ('HONEY_SUPER_1_2', 'Honey super 1/2'), ('QUEEN_EXCLUDER', 'Queen excluder'), ('BASE', 'Base'), ('HIVE_MAT', 'Hive Mat'), ('LID', 'Lid'), ('FEEDER', 'Feeder'), ('OTHER', 'Other')], max_length=16, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('TEMP', 'Temperature'), ('WEIGHT', 'Weight'), ('HUMIDITY', 'Humidity'), ('SOUND', 'Sound')], max_length=8)),
                ('last_reading', models.FloatField(blank=True, null=True)),
                ('authentication_token', models.CharField(max_length=255, unique=True)),
                ('token_last_refreshed', models.DateTimeField(auto_now_add=True)),
                ('hive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='apiary_central.hive')),
            ],
        ),
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('value', models.FloatField()),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='apiary_central.sensor')),
            ],
        ),
        migrations.AddField(
            model_name='hive',
            name='components',
            field=models.ManyToManyField(related_name='hives', to='apiary_central.hivecomponent'),
        ),
    ]
