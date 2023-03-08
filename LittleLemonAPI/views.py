from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from django.conf import settings
from django.shortcuts import get_object_or_404
from .permissions import IsManager


class ManagerUserList(generics.ListCreateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):        
        return User.objects.filter(groups__name=settings.MANAGER_GROUP_NAME)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
            manager_group.user_set.add(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # tested with invalid email address. it retruend "200 OK". 
        # return Response(serializer.errors)


class ManagerUserDetail(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_object(self):
        pk = self.kwargs.get('pk')
        print(pk)
        user = get_object_or_404(User, pk=pk)
        manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
        if not user.groups.filter(pk=manager_group.pk).exists():
            raise get_object_or_404
        return user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
        manager_group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)


class DeliveryCrewUserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):        
        return User.objects.filter(groups__name=settings.DELIVERYCREW_GROUP_NAME)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            deliverycrew_group = Group.objects.get(name=settings.DELIVERYCREW_GROUP_NAME)
            deliverycrew_group.user_set.add(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewUserDetail(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_object(self):
        pk = self.kwargs.get('pk')
        print(pk)
        user = get_object_or_404(User, pk=pk)
        deliverycrew_group = Group.objects.get(name=settings.DELIVERYCREW_GROUP_NAME)
        if not user.groups.filter(pk=deliverycrew_group.pk).exists():
            raise get_object_or_404
        return user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        deliverycrew_group = Group.objects.get(name=settings.DELIVERYCREW_GROUP_NAME)
        deliverycrew_group.user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
