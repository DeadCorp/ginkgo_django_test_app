from django.conf import settings
from django.db import models

from product.models import Product
from supplieraccount.models import SupplierAccount

STATUS_CHOICES = [
    ('NOTHING', 'Nothing'),
    ('OOS', 'Out of stock'),
    ('SUCCESS', 'Success'),
    ('WRONG_DATA', 'Product was added with invalid data'),
    ('WRONG_ITEM', 'Invalid product in cart'),
    ('ADDING_PROBLEM', 'Problem with adding'),
    ('WRONG_COUNT', 'This count not availability'),
    ('IN_PROGRESS', 'In progress...')
]


class Order(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, verbose_name='Supplier account')
    order_id = models.CharField(max_length=100, verbose_name='Order id', default='', blank=True)
    quantity = models.CharField(max_length=10, verbose_name='Order quantity', default='', blank=True)
    price = models.CharField(max_length=10, verbose_name='Order price', default='', blank=True)

    def __str__(self):
        return f'Order for product: {self.product}, user: {self.user}'


class OrderStatus(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Order', default=None)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='NOTHING', blank=True)

    def delete(self, using=None, keep_parents=False):
        obj = OrderStatus.objects.get(pk=self.pk)
        images = obj.orderstatusimage_set.all()
        for i in images:
            if i != 'status_image/':
                i.status_image.delete()
                i.delete()
        super(OrderStatus, self).delete()

    def __str__(self):
        return f'Status for product: {self.order.product} for user: {self.order.user}'


class OrderStatusImage(models.Model):
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='Order status', default=None)
    status_image = models.ImageField(upload_to='status_image', null=True, blank=True)
    tag = models.CharField(max_length=100, verbose_name='Tag', default='', blank=True)

    def __str__(self):
        return f'Image {self.tag} for  {self.order_status}'
