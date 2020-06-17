from django.urls import path

from order import views

app_name = 'order'
urlpatterns = [
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('display_my_orders/<str:product>', views.display_my_orders, name='display_my_orders'),
    path('order_status_image/<int:pk>/', views.StatusImageView.as_view(), name='order_status_image'),
]
