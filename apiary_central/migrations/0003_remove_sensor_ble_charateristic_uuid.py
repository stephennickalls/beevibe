# Generated by Django 4.2.7 on 2023-12-13 03:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiary_central', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sensor',
            name='ble_charateristic_uuid',
        ),
    ]
