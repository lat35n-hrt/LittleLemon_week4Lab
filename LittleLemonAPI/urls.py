from django.urls import path
from . import views

urlpatterns = [
    path('api/groups/manager/users/', views.ManagerUserList.as_view()),
    path('api/groups/manager/users/<int:pk>/', views.ManagerUserDetail.as_view()),
    path('api/groups/delivery-crew/users/', views.DeliveryCrewUserList.as_view()),
    path('api/groups/delivery-crew/users/<int:pk>/', views.DeliveryCrewUserDetail.as_view()),
]