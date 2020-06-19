from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product_id', 'name']
    ordering = ['sku']

    fields = ['sku', 'product_id', 'option_id', 'name', ('price', 'delivery_price'),
              'is_variant', 'variants_tag', ('brand', 'model', 'rating'), 'url',
              'description', 'category', ('available', 'available_count'),
              'img', 'supplier', 'delivery', 'shipping', 'store_pickup'
              ]

    search_fields = ['sku', 'product_id', 'name']
