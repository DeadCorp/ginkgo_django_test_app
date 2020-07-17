import re

from django.contrib.auth.models import User, Group
from rest_framework import viewsets


from api.serializer import ProductSerializer, TaskSerializer, SupplierAccountsSerializer, OrderSerializer, \
    UserSerializer, GroupSerializer, StatusSerializer
from order.models import Order, OrderStatus
from product.models import Product

from supplieraccount.models import SupplierAccount
from task.models import Task


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('supplier')
    serializer_class = ProductSerializer


class TaskViewSet(viewsets.ModelViewSet):

    serializer_class = TaskSerializer
    search_fields = ['id']
    ordering_fields = ['pk']

    def get_queryset(self):
        queryset = Task.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            user = User.objects.get(username=username)
            queryset = queryset.filter(user_id=user)
        return queryset


class SupplierAccountsViewSet(viewsets.ModelViewSet):
    search_fields = ['username', 'email']
    ordering_fields = ['pk', 'supplier', 'username', 'email']
    queryset = SupplierAccount.objects.all().order_by('-supplier')
    serializer_class = SupplierAccountsSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        username = self.request.query_params.get('username', None)
        product_sku = self.request.query_params.get('sku', None)
        if username is not None:
            user = User.objects.get(username=username)
            queryset = queryset.filter(user=user)
            if product_sku is not None:
                product = Product.objects.get(sku=product_sku)
                queryset = queryset.filter(user=user, product=product)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer

    search_fields = ['order__order_id', ]
    ordering_fields = ['order__order_id', 'order__account__username', 'order__account__email', 'order__price']

    def get_queryset(self):
        queryset = OrderStatus.objects.all()
        username = self.request.query_params.get('username', None)
        product_sku = self.request.query_params.get('sku', None)
        if product_sku is not None:
            sku = re.search(r'orders\/(.+)', product_sku)

            sku = sku.group(1) or None
        else:
            sku = None
        if username is not None:
            user = User.objects.get(username=username)
            queryset = queryset.filter(order__user=user)
            if sku is not None:
                product = Product.objects.get(sku__contains=sku)
                queryset = queryset.filter(order__user=user, order__product=product)
        return queryset
