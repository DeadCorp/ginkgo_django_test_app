from django.conf import settings
from django.db import models


class SupplierCodes(object):
    SUPPLIERS = {
        'WM': 'Walmart',
        'KM': 'Kmart',

    }

    def suppliers_dict_to_choices_tuple(self):
        return [(k, v) for k, v in self.SUPPLIERS.items()]


class SupplierAccount(models.Model):
    supplier = models.CharField(max_length=25, verbose_name='Supplier',
                                choices=SupplierCodes.suppliers_dict_to_choices_tuple(SupplierCodes), default='')
    username = models.CharField(max_length=30, verbose_name='Username', default='', blank=True)
    email = models.EmailField(max_length=30, verbose_name='Email', default='')
    password = models.CharField(max_length=30, verbose_name='Password', default='')

    def __str__(self):
        return f'Supplier: {self.supplier}, email: {self.email}'


class UserSupplierAccount(models.Model):
    # This model is to ensure that the supplier account does not change for all users,
    # when one of the users changes the account
    # For one supplier and one user can be selected only one supplier account
    supplier_account = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, verbose_name='Supplier account')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    is_selected_account = models.BooleanField(verbose_name='Selected account', default=False, blank=True)

    def __str__(self):
        return f'{self.supplier_account} for User: {self.user}'
