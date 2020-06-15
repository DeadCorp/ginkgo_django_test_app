from django.contrib import admin

from order.models import Order, OrderStatus


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['product', 'order_id', 'user']


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['order', 'status']
