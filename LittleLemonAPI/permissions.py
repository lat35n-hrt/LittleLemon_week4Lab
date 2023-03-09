from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()

def get_permissions(self):
    if self.request.method == 'GET':
        permission_classes = [IsAuthenticated]
    else:
        permission_classes = [IsAuthenticated, IsManager]
    return permission_classes