from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.core.paginator import Paginator
from cars.models import Car
from .models import ServiceRequest
from .forms import ServiceRequestForm, ServiceStatusUpdateForm
from accounts.forms import AdminCustomerEditForm

User = get_user_model()

def admin_required(view_func):
    """Decorator to restrict view to logged-in users with role='admin'."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, "Access denied. Administrator privileges required.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    """Decorator to restrict view to logged-in users with role='customer'."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'customer':
            messages.error(request, "Access denied. Customer privileges required.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
def dashboard_view(request):
    """Redirects users to their appropriate dashboard based on their role."""
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    return redirect('customer_dashboard')

@login_required
@admin_required
def admin_dashboard(request):
    """Displays key statistics and summary information for administrators."""
    customers_count = User.objects.filter(role='customer').count()
    cars_count = Car.objects.count()
    
    requests_qs = ServiceRequest.objects.all()
    pending_count = requests_qs.filter(status='Pending').count()
    in_progress_count = requests_qs.filter(status='In Progress').count()
    completed_count = requests_qs.filter(status='Completed').count()
    
    recent_requests = requests_qs.select_related('user', 'car').order_by('-id')[:5]
    
    context = {
        'customers_count': customers_count,
        'cars_count': cars_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'recent_requests': recent_requests,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@customer_required
def customer_dashboard(request):
    """Displays key statistics and summary information for a customer."""
    cars_count = Car.objects.filter(user=request.user).count()
    requests = ServiceRequest.objects.filter(user=request.user)
    requests_count = requests.count()
    pending_count = requests.filter(status='Pending').count()
    in_progress_count = requests.filter(status='In Progress').count()
    completed_count = requests.filter(status='Completed').count()
    
    recent_requests = requests.order_by('-id')[:5]

    context = {
        'cars_count': cars_count,
        'requests_count': requests_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'recent_requests': recent_requests,
    }
    return render(request, 'customer_dashboard.html', context)



@login_required
@customer_required
def request_service(request):
    """Allows customers to request a service for one of their registered cars."""
    # Check if user has registered at least one car first
    if not Car.objects.filter(user=request.user).exists():
        messages.warning(request, "Please register a car before requesting a service.")
        return redirect('add_car')

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST, user=request.user)
        if form.is_valid():
            service_req = form.save(commit=False)
            service_req.user = request.user
            service_req.save()
            messages.success(request, f"Service request for {service_req.car} submitted successfully!")
            return redirect('service_status')
        else:
            messages.error(request, "Failed to submit request. Please correct the errors.")
    else:
        form = ServiceRequestForm(user=request.user)
    return render(request, 'request_service.html', {'form': form})

@login_required
@customer_required
def service_status(request):
    """Allows customers to view the status of their service requests with filters and sorting."""
    status_filter = request.GET.get('status', '').strip()
    car_filter = request.GET.get('car', '').strip()
    sort_by = request.GET.get('sort', 'newest').strip()

    requests_qs = ServiceRequest.objects.filter(user=request.user)
    user_cars = Car.objects.filter(user=request.user)

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    if car_filter:
        requests_qs = requests_qs.filter(car_id=car_filter)

    if sort_by == 'oldest':
        requests_qs = requests_qs.order_by('id')
    else:
        requests_qs = requests_qs.order_by('-id')

    context = {
        'requests': requests_qs,
        'status_filter': status_filter,
        'car_filter': car_filter,
        'user_cars': user_cars,
        'sort_by': sort_by,
    }
    return render(request, 'service_status.html', context)

@login_required
@admin_required
def admin_customers(request):
    """Allows administrators to view all registered customers with search and pagination."""
    search_query = request.GET.get('q', '').strip()
    
    customers_qs = User.objects.filter(role='customer').annotate(cars_count=Count('cars')).order_by('id')

    if search_query:
        customers_qs = customers_qs.filter(
            Q(name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    paginator = Paginator(customers_qs, 10) # 10 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_customers.html', context)

@login_required
@admin_required
def admin_customer_detail(request, customer_id):
    """Displays detail panel/modal information for a specific customer."""
    customer = get_object_or_404(User, id=customer_id, role='customer')
    cars = Car.objects.filter(user=customer)
    requests = ServiceRequest.objects.filter(user=customer).order_by('-id')
    
    context = {
        'customer': customer,
        'cars': cars,
        'requests': requests,
    }
    return render(request, 'admin_customer_detail.html', context)

@login_required
@admin_required
def admin_customer_edit(request, customer_id):
    """Allows admin to update a customer's role or phone number."""
    customer = get_object_or_404(User, id=customer_id)
    if request.method == 'POST':
        form = AdminCustomerEditForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, f"Customer {customer.name} updated successfully.")
            return redirect('admin_customers')
        else:
            messages.error(request, "Failed to update customer. Please correct errors.")
    else:
        form = AdminCustomerEditForm(instance=customer)
    return render(request, 'admin_customer_edit.html', {'form': form, 'customer': customer})

@login_required
@admin_required
def admin_customer_delete(request, customer_id):
    """Allows administrators to delete a customer and all their registered data."""
    customer = get_object_or_404(User, id=customer_id, role='customer')
    if request.method == 'POST':
        customer_name = customer.name
        customer.delete()
        messages.success(request, f"Customer {customer_name} and all their registered vehicles/requests have been deleted.")
        return redirect('admin_customers')
    return render(request, 'admin_customer_delete_confirm.html', {'customer': customer})

@login_required
@admin_required
def admin_cars(request):
    """Allows administrators to view all registered cars across all customers."""
    cars = Car.objects.all().select_related('user').order_by('id')
    return render(request, 'admin_cars.html', {'cars': cars})

@login_required
@admin_required
def admin_service_requests(request):
    """Allows administrators to view all service requests with advanced filters, search, and pagination."""
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    service_filter = request.GET.get('service_type', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    requests_qs = ServiceRequest.objects.all().select_related('user', 'car')

    if search_query:
        requests_qs = requests_qs.filter(
            Q(user__name__icontains=search_query) |
            Q(car__car_number__icontains=search_query)
        )
    
    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)
        
    if service_filter:
        requests_qs = requests_qs.filter(service_type=service_filter)
        
    if start_date:
        requests_qs = requests_qs.filter(request_date__gte=start_date)
        
    if end_date:
        requests_qs = requests_qs.filter(request_date__lte=end_date)

    requests_qs = requests_qs.order_by('-id')

    paginator = Paginator(requests_qs, 10) # 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # For status update forms in rows
    status_choices = ServiceRequest.STATUS_CHOICES
    service_type_choices = [
        ('Oil Change', 'Oil Change'),
        ('Tyre Replacement', 'Tyre Replacement'),
        ('General Checkup', 'General Checkup'),
        ('Engine Repair', 'Engine Repair'),
        ('Other', 'Other')
    ]

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'service_filter': service_filter,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': status_choices,
        'service_type_choices': service_type_choices,
    }
    return render(request, 'admin_service_requests.html', context)

@login_required
@admin_required
def admin_update_status(request, request_id):
    """Allows administrators to update the status of a service request."""
    service_req = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        # If 'admin_message' is not in POST keys (inline update), preserve the existing message
        post_data = request.POST.copy()
        if 'admin_message' not in post_data:
            post_data['admin_message'] = service_req.admin_message or ''
            
        form = ServiceStatusUpdateForm(post_data, instance=service_req)
        if form.is_valid():
            updated_req = form.save()
            messages.success(request, f"Request #{service_req.id} status updated to '{service_req.status}' successfully.")
            
            # Send status update email notification on update
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Car Service Request #{updated_req.id} Update - {updated_req.car.car_brand} {updated_req.car.car_model}"
            message = f"Hello {updated_req.user.name},\n\n" \
                      f"Your service request for {updated_req.car.car_brand} {updated_req.car.car_model} " \
                      f"({updated_req.car.car_number}) has been updated by the administrator.\n\n" \
                      f"Current Status: {updated_req.status}\n\n"
            
            if updated_req.admin_message:
                message += f"Administrator Message/Notes:\n" \
                           f"----------------------------------------\n" \
                           f"{updated_req.admin_message}\n" \
                           f"----------------------------------------\n\n"
            
            message += f"You can view your full service log and history by logging into your dashboard.\n\n" \
                       f"Best regards,\n" \
                       f"CAR SERVICE MANAGEMENT SYSTEM Team"
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL or 'no-reply@csms.com',
                recipient_list=[updated_req.user.email],
                fail_silently=False
            )
            
            # Redirect to page referer if available, to preserve search results/filters
            next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'admin_service_requests'
            return redirect(next_url)
        else:
            messages.error(request, "Failed to update status.")
    else:
        form = ServiceStatusUpdateForm(instance=service_req)
    return render(request, 'admin_update_status.html', {'form': form, 'service_req': service_req})

@login_required
@admin_required
def delete_service_request(request, request_id):
    """Allows administrators to delete a service request from the registry."""
    service_req = get_object_or_404(ServiceRequest, id=request_id)
    if request.method == 'POST':
        req_id = service_req.id
        service_req.delete()
        messages.success(request, f"Service request #{req_id} deleted successfully.")
        return redirect('admin_service_requests')
    return render(request, 'admin_delete_request_confirm.html', {'req': service_req})
