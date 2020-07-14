from django.contrib.auth.models import User, Group
from rest_framework import serializers

from order.models import Order, OrderStatus
from product.models import Product
from supplieraccount.models import SupplierAccount
from task.models import Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    url_field_name = 'product_instance'

    class Meta:
        model = Product
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['pk', 'description']


class SupplierAccountsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SupplierAccount
        fields = ['url', 'pk', 'supplier', 'username', 'email', 'password']


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    product = serializers.SlugRelatedField(many=False, read_only=True, slug_field='sku')
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    account = SupplierAccountsSerializer(many=False)

    class Meta:
        model = Order
        fields = ['url', 'order_id', 'price', 'quantity', 'product', 'account', 'user']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    order = OrderSerializer(many=False)

    class Meta:
        model = OrderStatus
        fields = ['url', 'pk', 'status', 'order']
        datatables_always_serialize = ('pk', 'status',)
