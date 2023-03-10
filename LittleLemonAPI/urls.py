from django.urls import path
from . import views

urlpatterns = [
    path('api/groups/manager/users', views.ManagerUserList.as_view()),
    path('api/groups/manager/users/<int:pk>', views.ManagerUserDetail.as_view()),
    path('api/groups/delivery-crew/users', views.DeliveryCrewUserList.as_view()),
    path('api/groups/delivery-crew/users/<int:pk>', views.DeliveryCrewUserDetail.as_view()),
    path('api/menu-items', views.MenuItemList.as_view()),
    path('api/menu-items/<int:pk>', views.MenuItemDetail.as_view()),
    path('api/categories', views.CategoryList.as_view()),
    path('api/orders', views.OrderList.as_view()),
    path('api/orders/<int:pk>', views.OrderDetail.as_view()),
    path('api/cart/orders', views.CartOrder.as_view()),
]