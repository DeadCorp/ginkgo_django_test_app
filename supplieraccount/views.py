from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views import generic

from supplieraccount.forms import SupplierAccountForm
from supplieraccount.models import SupplierAccount, SupplierCodes, UserSupplierAccount


class SupplierAccountView(generic.ListView):
    model = SupplierAccount
    context_object_name = 'accounts'
    template_name = 'supplieraccount/supplier_accounts.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        # get dictionary with suppliers to sort accounts of suppliers by supplier code
        suppliers = SupplierCodes.SUPPLIERS
        context['suppliers'] = suppliers
        context['accounts'] = self.sort_supplier_account_by_suppliers(suppliers)
        context['user_selected_accounts'] = self.sort_user_supplier_account_by_suppliers(suppliers)
        return context

    def sort_supplier_account_by_suppliers(self, suppliers):
        # Return dictionary where:
        # key is the Suppliers code
        # value is the queryset  with all suppliers accounts, without accounts that have been selected by the user
        return {supplier_code: SupplierAccount.objects.filter(supplier=supplier_code).exclude(
            usersupplieraccount__user=self.request.user,
            usersupplieraccount__is_selected_account=True) for supplier_code in suppliers}

    def sort_user_supplier_account_by_suppliers(self, suppliers):
        # Return dictionary where:
        # key is the Suppliers code
        # value is the queryset  with accounts that have been selected by the user
        # this records always will be first in the view
        return {supplier_code: UserSupplierAccount.objects.filter(
            user=self.request.user, supplier_account__supplier=supplier_code) for supplier_code in suppliers}


@login_required()
def add_supplier_account(request):
    if request.method == 'POST':
        form = SupplierAccountForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get('next'):
                return redirect(request.POST.get('next'))
            else:
                return redirect('supplier_account:supplier_accounts')
        else:
            print(form.errors)
    else:
        form = SupplierAccountForm()

    return render(request, 'supplieraccount/add_supplier_account.html', {'form': form})


@login_required()
def delete_supplier_account(request):
    if request.method == 'POST':
        supplier_account_id = request.POST.get('supplier_account_id')
        try:
            supplier = SupplierAccount.objects.get(pk=supplier_account_id)
            supplier.delete()
        except SupplierAccount.DoesNotExist:
            pass

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def select_supplier_account(request):
    if request.method == 'POST':
        supplier_account_id = request.POST.get('supplier_account_id')
        account_to_select = SupplierAccount.objects.get(pk=supplier_account_id)
        delete_user_supplier_account(request.user, account_to_select.supplier)
        select_account = UserSupplierAccount(supplier_account=account_to_select, user=request.user,
                                             is_selected_account=True)
        select_account.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_user_supplier_account(user, supplier):
    # try delete selected supplier account for user
    try:
        user_account_already_selected = UserSupplierAccount.objects.get(
            supplier_account__supplier=supplier, user=user, is_selected_account=True)
        user_account_already_selected.delete()
    except UserSupplierAccount.DoesNotExist:
        pass
