from django.urls import path
from . import views

urlpatterns = [
    path('api/groups/manager/users/', views.ManagerUserList.as_view()),
    path('api/groups/manager/users/<int:user_id>/', views.ManagerUserDetail.as_view()),
    path('api/groups/delivery-crew/users/', views.DeliveryCrewUserList.as_view()),
    path('api/groups/delivery-crew/users/<int:user_id>/', views.DeliveryCrewUserDetail.as_view()),
]