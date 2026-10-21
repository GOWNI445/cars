from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_cars, name='my_cars'),
    path('add/', views.add_car, name='add_car'),
    path('edit/<int:car_id>/', views.edit_car, name='edit_car'),
    path('delete/<int:car_id>/', views.delete_car, name='delete_car'),
]
