from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('INDIVIDUAL', 'Individual'),
        ('COMMERCIAL', 'Commercial'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='INDIVIDUAL')
    email = models.EmailField(unique=True)
    receive_notifications = models.BooleanField(default=True)  # Simple notification preference

    def __str__(self):
        return self.username
