from rest_framework.authtoken.models import Token

from .models import SupplierAccount, SupplierCodes


def suppliers_and_accounts(request):
    if not request.user.is_anonymous:
        return {'token': Token.objects.get(user=request.user),
                'suppliers': SupplierCodes.SUPPLIERS,
                'all_supplier_accounts': {supplier_code: SupplierAccount.objects.filter(supplier=supplier_code)
                                          for supplier_code in SupplierCodes.SUPPLIERS}}
    else:
        return {'suppliers': {},
                'all_supplier_accounts': {},
                }
