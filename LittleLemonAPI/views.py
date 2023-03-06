from django.contrib.auth.models import User, Group
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer


class ManagerUserList(generics.ListCreateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):        
        return User.objects.filter(groups__name='Manager')


        # manager_group = Group.objects.get(name='Manager')
        # return User.objects.filter(groups=manager_group)

 

class ManagerUserDetail(APIView):
    ()


class DeliveryCrewUserList(APIView):
    ()


class DeliveryCrewUserDetail(APIView):
    ()
