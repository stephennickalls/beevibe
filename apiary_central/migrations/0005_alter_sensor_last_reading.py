# Generated by Django 4.2.6 on 2023-11-12 19:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiary_central', '0004_alter_apiaryhub_last_connected_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='last_reading',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(400.0)]),
        ),
    ]