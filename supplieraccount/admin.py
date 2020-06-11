from django.contrib import admin

from supplieraccount.models import SupplierAccount, UserSupplierAccount


@admin.register(SupplierAccount)
class SupplierAccountAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'email']
    ordering = ['supplier']


@admin.register(UserSupplierAccount)
class SupplierAccountAdmin(admin.ModelAdmin):
    list_display = ['supplier_account', 'user', 'is_selected_account']
    ordering = ['supplier_account']
