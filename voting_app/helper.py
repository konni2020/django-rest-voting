from rest_framework import permissions
from django.contrib.auth.models import User


class OnlyOwnerCanUpdateOrDelete(permissions.BasePermission):

    # def has_permission(self, request, view):
    #     if request.method in ['PUT', 'PATCH', 'DELETE']:
    #         user = User.objects.get(pk=view.kwargs['pk'])
    #         return request.user == user
    #     return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.name == request.user.username