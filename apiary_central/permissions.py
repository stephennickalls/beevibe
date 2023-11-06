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
    Custom permission to only allow owners of an apiary to create an apiary hub for it.
    """

    def has_permission(self, request, view):
        if request.user.is_staff:  # Allow staff to access everything
            return True

        # Get the apiary ID from the request data
        apiary_id = request.data.get('apiary')
        
        # Check if the apiary ID is provided in the request data
        if apiary_id is None:
            return False  # Or handle how you would like if the apiary is not provided
        
        # Check if the apiary exists and is owned by the requesting user
        try:
            apiary = Apiary.objects.get(pk=apiary_id, owner=request.user)
        except Apiary.DoesNotExist:
            return False

        return True