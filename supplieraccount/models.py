from django.conf import settings
from django.db import models


class SupplierCodes(object):
    SUPPLIERS = {
        'WM': 'Walmart',
        'KM': 'Kmart',
        'SC': 'SamsClub',

    }

    def suppliers_dict_to_choices_tuple(self):
        return [(k, v) for k, v in self.SUPPLIERS.items()]


class SupplierAccount(models.Model):
    supplier = models.CharField(max_length=25, verbose_name='Supplier',
                                choices=SupplierCodes.suppliers_dict_to_choices_tuple(SupplierCodes()), default='')
    username = models.TextField(verbose_name='Username', default='', blank=True)
    email = models.EmailField(verbose_name='Email', default='')
    password = models.TextField(verbose_name='Password', default='')

    def save(self):
        # if for supplier exist account with this email, notify user about it
        try:
            exist = SupplierAccount.objects.get(supplier=self.supplier, email=self.email)
        except SupplierAccount.DoesNotExist:
            super(SupplierAccount, self).save()

    def __str__(self):
        return f'ID - {self.pk}; Supplier: {self.supplier}; ' \
               f'Username: {self.username}; Email: {self.email}'
