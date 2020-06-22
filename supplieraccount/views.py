from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views import generic

from supplieraccount.forms import SupplierAccountForm
from supplieraccount.models import SupplierAccount, SupplierCodes


class SupplierAccountView(generic.ListView):
    model = SupplierAccount
    context_object_name = 'accounts'
    template_name = 'supplieraccount/supplier_accounts.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # get dictionary with suppliers to sort accounts of suppliers by supplier code
        suppliers = SupplierCodes.SUPPLIERS
        context['accounts'] = self.sort_supplier_account_by_suppliers(suppliers)
        return context

    @staticmethod
    def sort_supplier_account_by_suppliers(suppliers):
        # Return dictionary where:
        # key is the Suppliers code
        # value is the queryset  with all suppliers accounts
        return {supplier_code: SupplierAccount.objects.filter(supplier=supplier_code) for supplier_code in suppliers}


@login_required()
def add_supplier_account(request):
    if request.method == 'POST':
        form = SupplierAccountForm(request.POST)
        if form.is_valid():
            form.save()
            if form.instance.id is None:
                form.add_error(None, 'This email is already used for this supplier')
                form.initial['supplier'] = request.POST.get('supplier')
                return render(request, 'supplieraccount/add_supplier_account.html', {'form': form})
            if request.POST.get('next'):
                return HttpResponseRedirect(request.POST['next'])
            else:
                return redirect('supplier_account:supplier_accounts')
    else:
        if request.path != 'supplier_account:add_supplier_account':
            form = SupplierAccountForm(initial={'supplier': request.GET.get('supplier')})
        else:
            form = SupplierAccountForm()
    return render(request, 'supplieraccount/add_supplier_account.html', {'form': form})
