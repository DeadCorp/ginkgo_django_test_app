from .models import SupplierAccount, SupplierCodes


def selected_supplier_accounts(request):
    if not request.user.is_anonymous:
        accounts = SupplierAccount.objects.filter(usersupplieraccount__user=request.user)
        if len(accounts) == 0:
            return {'selected_supplier_accounts': None,
                    'suppliers': SupplierCodes.SUPPLIERS,
                    'all_supplier_accounts': SupplierAccount.objects.all()}
        else:

            return {'selected_supplier_accounts': {supplier_code: SupplierAccount.objects.filter(supplier=supplier_code,
                                                                                                 usersupplieraccount__user=request.user)
                                                   for supplier_code in SupplierCodes.SUPPLIERS},
                    'suppliers': SupplierCodes.SUPPLIERS,
                    'all_supplier_accounts': SupplierAccount.objects.all()}
    else:
        return {'selected_supplier_accounts': None,
                'suppliers': SupplierCodes.SUPPLIERS,
                'all_supplier_accounts': SupplierAccount.objects.all()}
