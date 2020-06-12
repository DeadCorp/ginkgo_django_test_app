from django.urls import path

from product import views

app_name = 'product'
urlpatterns = [
    path('', views.ProductListView.as_view(), name='products'),
    path('<str:pk>/', views.ProductDetailView.as_view(), name='detail'),
]
