from django.contrib.auth.decorators import login_required
from django.urls import path

from supplieraccount import views

app_name = 'supplier_account'
urlpatterns = [
    path('', login_required(views.SupplierAccountView.as_view()), name='supplier_accounts'),
    path('add_supplier_account/', views.add_supplier_account, name='add_supplier_account'),
    path('delete_supplier_account/', views.delete_supplier_account, name='delete_supplier_account'),
    path('select_supplier_account/', views.select_supplier_account, name='select_supplier_account'),


]
