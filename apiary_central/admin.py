from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from core.models import CustomUser


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'username', 'is_staff', 'active', 'last_payment_date']
    search_fields = ['username__istartswith']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('user_type', 'receive_notifications', 'active', 'end_date', 'trial_end_date', 'last_payment_date', 'subscription_id')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'user_type', 'receive_notifications', 'active', 'end_date', 'trial_end_date', 'last_payment_date', 'subscription_id'),
        }),
    )

@admin.register(models.Apiary)
class ApiaryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['owner']
    list_display = ['id', 'name', 'latitude', 'longitude', 'description', 'registration_number', 'owner']
    list_per_page = 10
    search_fields = ['name__istartswith']

@admin.register(models.ApiaryHub)
class ApiaryHubAdmin(admin.ModelAdmin):
    autocomplete_fields = ['apiary']
    model = models.ApiaryHub
    list_display = ['id', 'api_key', 'created_at', 'type', 'end_date', 'last_connected_at', 'battery_level', 'software_version', 'description']
    list_per_page = 10

@admin.register(models.HiveComponentType)
class HiveComponentTypeAdmin(admin.ModelAdmin):
    model = models.HiveComponentType
    search_fields = ['name__istartswith']

class HiveComponentInline(admin.TabularInline):
    autocomplete_fields = ['type']
    model = models.HiveComponent
    extra = 1  # Number of empty forms to display

@admin.register(models.Hive)
class HiveAdmin(admin.ModelAdmin):
    inlines = [
        HiveComponentInline
    ]
    autocomplete_fields = ['apiary']
    list_display = ['name', 'description', 'apiary']
    search_fields = ['name']
    exclude = ('components',)

@admin.register(models.HiveComponent)
class HiveComponentAdmin(admin.ModelAdmin):
    list_display = ['type', 'description']
    search_fields = ['type__name']  # Allow searching by component type's name
    ordering = ['type']
    list_per_page = 10

@admin.register(models.SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_per_page = 10

@admin.register(models.Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'sensor_type', 'created_at', 'last_reading', 'hive']
    autocomplete_fields = ['hive', 'sensor_type']
    search_fields = ['uuid', 'sensor_type__name']
    list_per_page = 10

@admin.register(models.DataTransmission)
class DataTransmissionAdmin(admin.ModelAdmin):
    list_display = ['transmission_uuid', 'apiary', 'transmission_tries', 'start_timestamp', 'end_timestamp']
    search_fields = ['transmission_uuid__istartswith']
                    

@admin.register(models.SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'transmission', 'timestamp', 'value']
    autocomplete_fields = ['sensor', 'transmission']
    search_fields = ['sensor__uuid', 'transmission__uuid']
    list_per_page = 10