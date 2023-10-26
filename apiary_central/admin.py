from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
from core.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'username', 'email', 'active', 'last_payment_date']
    search_fields = ['username__istartswith']
    list_per_page = 10
    ordering = ['first_name', 'last_name']

@admin.register(models.Apiary)
class ApiaryAdmin(admin.ModelAdmin):
    autocomplete_fields = ['owner']
    list_display = ['id', 'name', 'latitude', 'longitude', 'description', 'registration_number', 'owner']
    list_per_page = 10
    search_fields = ['name__istartswith']

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

class SensorAdmin(admin.ModelAdmin):
    pass