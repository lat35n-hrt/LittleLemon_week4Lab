from django.urls import path
from . import views

urlpatterns = [
    path('groups/manager/users', views.ManagerUserList.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerUserDetail.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewUserList.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewUserDetail.as_view()),
    path('menu-items', views.MenuItemList.as_view()),
    path('menu-items/<int:pk>', views.MenuItemDetail.as_view()),
    path('categories', views.CategoryList.as_view()),
    path('orders', views.OrderList.as_view()),
    path('orders/<int:pk>', views.OrderDetail.as_view()),
    path('cart/orders', views.CartOrder.as_view()),
    path('cart/orders/menu-items', views.CartMenuItems.as_view()),
]