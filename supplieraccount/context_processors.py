from .models import SupplierAccount, SupplierCodes


def suppliers_and_accounts(request):
    if not request.user.is_anonymous:
        return {'suppliers': SupplierCodes.SUPPLIERS,
                'all_supplier_accounts': {supplier_code: SupplierAccount.objects.filter(supplier=supplier_code)
                                          for supplier_code in SupplierCodes.SUPPLIERS}}
