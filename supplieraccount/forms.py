from django import forms
from django.forms import ModelForm

from supplieraccount.models import SupplierAccount


class SupplierAccountForm(ModelForm):

    username = forms.CharField(max_length=30, required=False)

    class Meta:
        model = SupplierAccount
        fields = ['supplier', 'username', 'email', 'password']

