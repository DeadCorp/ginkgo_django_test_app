from django.urls import path

from task import views

app_name = 'task'
urlpatterns = [
    path('refresh_product_data/<str:sku>/', views.refresh_product_data, name='refresh_product_data'),
    path('add_task', views.add_task, name='add_task'),
    path('delete_task', views.delete_task, name='delete_task'),
    path('retry_task/<str:pk>', views.retry_task, name='retry_task'),
    path('task_gen_csv/<str:pk>', views.task_gen_csv, name='task_gen_csv'),
    path('task_gen_xls/<str:pk>', views.task_gen_xls, name='task_gen_xls'),
    path('get_tasks_json/', views.get_tasks_json, name='get_tasks_json'),
]
