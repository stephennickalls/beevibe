# Generated by Django 4.2.6 on 2023-10-17 00:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apiary_central', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensor',
            name='hive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensors', to='apiary_central.hive'),
        ),
    ]
