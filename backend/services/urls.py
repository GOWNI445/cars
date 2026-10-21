from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('request/', views.request_service, name='request_service'),
    path('status/', views.service_status, name='service_status'),
    path('admin/customers/', views.admin_customers, name='admin_customers'),
    path('admin/customers/<int:customer_id>/', views.admin_customer_detail, name='admin_customer_detail'),
    path('admin/customers/<int:customer_id>/edit/', views.admin_customer_edit, name='admin_customer_edit'),
    path('admin/customers/<int:customer_id>/delete/', views.admin_customer_delete, name='admin_customer_delete'),
    path('admin/cars/', views.admin_cars, name='admin_cars'),
    path('admin/requests/', views.admin_service_requests, name='admin_service_requests'),
    path('admin/requests/<int:request_id>/update/', views.admin_update_status, name='admin_update_status'),
    path('admin/requests/<int:request_id>/delete/', views.delete_service_request, name='admin_delete_service_request'),
]
