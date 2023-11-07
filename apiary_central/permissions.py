from rest_framework import permissions
from .models import Apiary


class IsHiveOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:  # Allow staff to access everything
            return True

        # For non-staff users, check ownership
        user = request.user
        apiary_id = view.kwargs['apiary_pk']

        try:
            apiary = Apiary.objects.get(id=apiary_id, owner=user)
            return True
        except Apiary.DoesNotExist:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:  # Allow staff to access everything
            return True

        # For non-staff users, check ownership of the object
        user = request.user
        return obj.apiary.owner == user
    

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
            # print(f'################## user from test: {request.user}')
            apiary_id = request.data.get('apiary')
            # print(f'################## apiary id from test: {apiary_id}')
            if apiary_id is None:
                # If there's no apiary ID in the request, deny permission
                return False
            
            # Check if the apiary exists and is owned by the requesting user
            try:
                apiary = Apiary.objects.get(pk=apiary_id)
                # print(f'################## apiary object from db: {apiary}')
                # print(f'################## return boolean result: {apiary.owner == request.user}')
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


