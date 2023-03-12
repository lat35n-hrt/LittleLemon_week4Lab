from rest_framework.permissions import BasePermission, IsAuthenticated
from django.conf import settings

from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=settings.DELIVERYCREW_GROUP_NAME).exists()

def get_permissions(self):
    if self.request.method == 'GET':
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsAuthenticated, IsManager]
    return [permission() for permission in permission_classes]