from django.db import models


class Product(models.Model):

    sku = models.CharField(max_length=100, verbose_name='Product SKU', primary_key=True)
    product_id = models.CharField(max_length=100, verbose_name='Supplier product id', default='', blank=True)
    option_id = models.CharField(max_length=100, verbose_name='Supplier option id', default='', blank=True)
    name = models.CharField(max_length=100, verbose_name='Product name', default='', blank=True)
    price = models.CharField(max_length=50, verbose_name='Price', default='', blank=True)
    url = models.CharField(max_length=100, verbose_name='Url', default='', blank=True)
    category = models.CharField(max_length=100, verbose_name='Category', default='', blank=True)
    rating = models.CharField(max_length=25, verbose_name='Rating', default='', blank=True)
    available = models.CharField(max_length=25, verbose_name='Availability', default='', blank=True)
    brand = models.CharField(max_length=25, verbose_name='Brand', default='', blank=True)
    available_count = models.CharField(max_length=10, verbose_name='Available count', default='', blank=True)
    delivery_price = models.CharField(max_length=10, verbose_name='Delivery price', default='', blank=True)
    variants_tag = models.CharField(max_length=100, verbose_name='Variants', default='', blank=True)
    img = models.CharField(max_length=100, verbose_name='Image', default='', blank=True)
    supplier = models.CharField(max_length=2, verbose_name='Supplier', default='', blank=True)
    model = models.CharField(max_length=25, verbose_name='Model', default='', blank=True)
    description = models.TextField(verbose_name='Description', default='', blank=True)
    is_variant = models.BooleanField(verbose_name='Is variance product', default=False, blank=True)
    delivery = models.BooleanField(verbose_name='Delivery', default=False, blank=True)
    shipping = models.BooleanField(verbose_name='Shipping', default=False, blank=True)
    store_pickup = models.BooleanField(verbose_name='Store pickup', default=False, blank=True)

    def __str__(self):
        return self.sku

