from django.contrib.auth.models import User, Group
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import UserSerializer, MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .permissions import IsManager, get_permissions, IsDeliveryCrew, IsAdminUser


class ManagerUserList(generics.ListCreateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_queryset(self):        
        return User.objects.filter(groups__name=settings.MANAGER_GROUP_NAME)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        if username:
            user = User.objects.get(username=username)
            manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
            manager_group.user_set.add(user)
            serializer = self.get_serializer(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({'error': 'Username not provided.'}, status=status.HTTP_400_BAD_REQUEST)


class ManagerUserDetail(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=pk)
        manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
        if not user.groups.filter(pk=manager_group.pk).exists():
            raise Http404('User does not belong to manager group')
        return user

    # delete Manager permission
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        manager_group = Group.objects.get(name=settings.MANAGER_GROUP_NAME)
        manager_group.user_set.remove(user)
        return Response({'message': 'Removed Manager permission successfully'}, status=status.HTTP_200_OK)


class DeliveryCrewUserList(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManager]

    def get_queryset(self):        
        return User.objects.filter(groups__name=settings.DELIVERYCREW_GROUP_NAME)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        if username:
            user = User.objects.get(username=username)
            delivery_crew_group = Group.objects.get(name=settings.DELIVERYCREW_GROUP_NAME)
            delivery_crew_group.user_set.add(user)
            serializer = self.get_serializer(user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({'error': 'Username not provided.'}, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated, IsAdminUser]

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
    permission_classes = [IsAuthenticated, IsAdminUser]

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

class OrderList(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if IsAdminUser().has_permission(self.request, self):
            return Order.objects
        elif IsManager().has_permission(self.request, self):
            return Order.objects
        elif IsDeliveryCrew().has_permission(self.request, self):
            return Order.objects.filter(delivery_crew=self.request.user)
        else:
            return Order.objects.filter(user=self.request.user)

    def create_order(self, request):

        cart_items = Cart.objects.filter(user=request.user)
        order = Order.objects.create(user=request.user, total=0, status=False)

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.menuitem.price,
                price=cart_item.quantity * cart_item.menuitem.price
            )

        order.total = sum(item.price for item in order.orderitem_set.all())
        order.save()

        cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    # No need for Customer to PUT and PATCH here

    def get_object(self):
        if IsManager().has_permission(self.request, self):
            try:
                order = Order.objects.get(pk=self.kwargs['pk'])
            except Order.DoesNotExist:
                raise Http404("Order does not exist.")
            return order
        elif IsDeliveryCrew().has_permission(self.request, self):
            pass
        else:
        #isCustomer    
            try:
                order = Order.objects.get(pk=self.kwargs['pk'])
            except Order.DoesNotExist:
                raise Http404("Order does not exist.")
            if order.user != self.request.user:
                raise PermissionDenied("You don't have permission to access this order.", code=404)
            return order

    def put(self, request, *args, **kwargs):
        if IsManager().has_permission(request, self):
            delivery_crew_id = request.data.get('delivery_crew')
            if delivery_crew_id:
                try:
                    delivery_crew = User.objects.get(pk=delivery_crew_id)
                except User.DoesNotExist:
                    return Response({"detail": "Delivery crew does not exist."}, status=status.HTTP_404_NOT_FOUND)
                self.get_object().delivery_crew = delivery_crew
                if self.get_object().status == 0:
                    self.get_object().status = 1
            else:
                self.get_object().status = request.data.get('status', self.get_object().status)
            self.get_object().save()
            return Response(self.serializer_class(self.get_object()).data)
        else:
            return Response({'message': 'Access denied'})

    def patch(self, request, *args, **kwargs):
        if IsManager().has_permission(request, self):
            delivery_crew_id = request.data.get('delivery_crew')
            print('delivery_crew_id:' + str(delivery_crew_id))
            if delivery_crew_id:
                try:
                    delivery_crew = User.objects.get(pk=delivery_crew_id)
                except User.DoesNotExist:
                    return Response({"detail": "Delivery crew does not exist."}, status=status.HTTP_404_NOT_FOUND)
                self.get_object().delivery_crew = delivery_crew
            self.get_object().status = request.data.get('status', self.get_object().status)
            if self.get_object().status == 0:
                self.get_object().status = 1
            self.get_object().save()
            return Response(self.serializer_class(self.get_object()).data)     
        elif IsDeliveryCrew().has_permission(request, self):
            delivery_crew_id = request.user.id
            print("debug now")
            print(delivery_crew_id)
            if self.get_object().delivery_crew is None:
                return Response({"detail": "No delivery crew is assigned to this order."}, status=status.HTTP_404_NOT_FOUND)
            if self.get_object().delivery_crew == delivery_crew_id:
                self.get_object().status = int(request.data.get('status', self.get_object().status))
                self.get_object().save()
                return Response(self.serializer_class(self.get_object()).data)
            else:
                return Response({"detail": "You are not assigned to this order."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'Access denied'})

    def delete(self, request, *args, **kwargs):
        if IsManager().has_permission(request, self):
            order = self.get_object()
            order.delete()
            return Response({"detail": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)    
        else:
            return Response({'message': 'Access denied'})


class CartOrder(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pass
    # def get_queryset(self):
    #     return Order.objects.filter(user=self.request.user)