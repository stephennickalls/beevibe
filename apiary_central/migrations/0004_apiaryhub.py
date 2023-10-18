# Generated by Django 4.2.6 on 2023-10-18 19:42

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apiary_central', '0003_alter_sensor_token_last_refreshed_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiaryHub',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=20)),
                ('end_date', models.DateField(default=datetime.date(2099, 12, 31))),
                ('status', models.CharField(choices=[('ONLINE', 'Online'), ('OFFLINE', 'Offline'), ('LOW_BATTERY', 'Low Battery')], default='OFFLINE', max_length=20)),
                ('last_connected_at', models.DateTimeField(blank=True, null=True)),
                ('battery_level', models.PositiveIntegerField(blank=True, null=True)),
                ('software_version', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('apiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hubs', to='apiary_central.apiary')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hubs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
