from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('INDIVIDUAL', 'Individual'),
        ('COMMERCIAL', 'Commercial'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='INDIVIDUAL')
    email = models.EmailField(unique=True)
    receive_notifications = models.BooleanField(default=True)  # Simple notification preference
    active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    end_date = models.DateField(default=date(2099, 12, 31))
    trial_end_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
    
class EmailConfirmation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    confirmation_token = models.CharField(max_length=100)
    token_created_date = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

