from django.urls import path

from order import views

app_name = 'order'
urlpatterns = [
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('display_my_orders/<str:product_sku>', views.display_my_orders, name='display_my_orders'),
    path('order_status_image/<int:pk>/', views.StatusImageView.as_view(), name='order_status_image'),
    path('order_gen_csv/', views.order_gen_csv, name='order_gen_csv'),
    path('order_gen_xls/', views.order_gen_xls, name='order_gen_xls'),
    path('display_all_orders/', views.display_all_orders, name='display_all_orders'),
]
