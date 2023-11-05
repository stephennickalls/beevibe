from rest_framework import permissions
from .models import Apiary


class BaseOwnerPermission(permissions.BasePermission):
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