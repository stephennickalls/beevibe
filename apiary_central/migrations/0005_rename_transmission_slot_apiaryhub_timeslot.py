# Generated by Django 4.2.7 on 2023-12-14 05:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiary_central', '0004_rename_slot_indicator_transmissiontimeslot_timeslot'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apiaryhub',
            old_name='transmission_slot',
            new_name='timeslot',
        ),
    ]