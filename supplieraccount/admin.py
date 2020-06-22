from django.contrib import admin

from supplieraccount.models import SupplierAccount


@admin.register(SupplierAccount)
class SupplierAccountAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'email']
    ordering = ['supplier']

