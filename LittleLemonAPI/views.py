from django.contrib.auth.models import User, Group
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError
from .models import MenuItem, Category, Cart
from .serializers import UserSerializer, MenuItemSerializer, CategorySerializer, CartSerializer
from .permissions import IsManager, get_permissions


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


class DeliveryCrewUserDetail(generics.RetrieveDestroyAPIView):
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


class MenuItemList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager]
        return [permission() for permission in permission_classes]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
  
    def get_permissions(self):
        return get_permissions(self)

    def get_object(self):
        try:
            return MenuItem.objects.get(id=self.kwargs['pk'])
        except MenuItem.DoesNotExist:
            raise NotFound()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryList(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_permissions(self):
        return get_permissions(self, self)

    def get_queryset(self):
        return Category.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartMenuItems(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        cart_items.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)