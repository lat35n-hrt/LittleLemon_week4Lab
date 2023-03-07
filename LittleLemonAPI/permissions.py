from rest_framework.permissions import BasePermission
from django.conf import settings

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()