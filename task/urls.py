from django.urls import path

from task import views

app_name = 'task'
urlpatterns = [
    path('refresh_product_data/<str:sku>/', views.refresh_product_data, name='refresh_product_data'),
    path('add_task', views.add_task, name='add_task'),
    path('delete_task', views.delete_task, name='delete_task'),
]
