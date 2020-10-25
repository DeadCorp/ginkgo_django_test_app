from django.contrib.auth.decorators import login_required
from django.urls import path

from supplieraccount import views

app_name = 'supplier_account'
urlpatterns = [
    path('', views.supplier_accounts, name='supplier_accounts'),
    path('add_supplier_account/', views.add_supplier_account, name='add_supplier_account'),
]
