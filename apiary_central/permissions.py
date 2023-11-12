from django.forms import ValidationError
from rest_framework import permissions
from .models import Apiary, Hive


class IsHiveOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:  # Allow staff to access everything
            return True

        if 'apiary_pk' in view.kwargs:
            return self.check_apiary_ownership(request.user, view.kwargs['apiary_pk'])
        elif 'hive' in request.data:
            return self.check_hive_ownership(request.user, request.data['hive'])

        return True  # Default to True if neither condition is met

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:  # Allow staff to access everything
            return True

        return obj.apiary.owner == request.user

    def check_apiary_ownership(self, user, apiary_id):
        try:
            apiary = Apiary.objects.get(id=apiary_id, owner=user)
            return True
        except Apiary.DoesNotExist:
            return False

    def check_hive_ownership(self, user, hive_id):
        try:
            hive = Hive.objects.get(id=hive_id)
            return hive.apiary.owner == user
        except Hive.DoesNotExist:
            return False
    

class IsApiaryOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an apiary to access or modify an apiary hub for it.
    """

    def has_permission(self, request, view):
        # Staff users can do anything
        if request.user.is_staff:
            return True

        # Safe methods are always allowed
        if request.method in permissions.SAFE_METHODS:
            return True

        # For methods that create or modify resources, check ownership
        if request.method in ['POST', 'PUT', 'PATCH']:
            apiary_id = request.data.get('apiary')
            if apiary_id is None:
                # If there's no apiary ID in the request, deny permission
                return False
            
            # Check if the apiary exists and is owned by the requesting user
            try:
                apiary = Apiary.objects.get(pk=apiary_id)
                return apiary.owner == request.user
            except Apiary.DoesNotExist:
                # If the apiary doesn't exist, deny permission
                return False

        # Allow DELETE requests to pass through to has_object_permission
        if request.method in ['DELETE']:
            return True

        # If none of the above conditions are met, deny permission
        return False


    def has_object_permission(self, request, view, obj):
        # print('has_object_permission called')
        # Staff users can do anything
        if request.user.is_staff:
            return True

        # Owners can read their own objects
        if request.method in permissions.SAFE_METHODS:
            return obj.apiary.owner == request.user

        # Owners can delete or update their own objects
        if request.method in ['DELETE', 'PATCH']:
            return obj.apiary.owner == request.user

        # By default, no other actions are allowed
        return False


