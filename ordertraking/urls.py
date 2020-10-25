from django.urls import path

from ordertraking import views

app_name = 'order_tracking'
urlpatterns = [
    path('', views.track_order, name='track_order'),

]
