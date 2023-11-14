# Generated by Django 4.2.6 on 2023-11-14 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiary_central', '0009_rename_apiaryhub_datatransmission_apiary_hub'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataTransmissionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
