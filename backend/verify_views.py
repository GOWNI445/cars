import os
import django
from django.test import Client
from django.urls import reverse

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_service_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from cars.models import Car
from services.models import ServiceRequest

User = get_user_model()

def run_tests():
    c = Client()
    print("=================== STARTING FUNCTIONAL TESTS ===================")
    
    # 1. Public Pages
    print("\n[1] Testing Public Pages:")
    
    # Home Page
    response = c.get('/')
    print(f"  GET '/' (Home): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Home page failed to load"
    
    # Login Page
    response = c.get('/login/')
    print(f"  GET '/login/': Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Login page failed to load"
    
    # Register Page
    response = c.get('/register/')
    print(f"  GET '/register/': Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Register page failed to load"


    # 2. Authentication and Customer Access
    print("\n[2] Testing Customer Authentication & Views:")
    
    # Log in John Doe
    login_success = c.login(username='john@example.com', password='customerpassword')
    print(f"  Login john@example.com: Result = {login_success} (Expected True)")
    assert login_success, "Customer login failed"
    
    # Redirect Dashboard
    response = c.get('/services/dashboard/', follow=True)
    print(f"  GET '/services/dashboard/' (Redirect check): Final Path = '{response.resolver_match.view_name}' (Expected 'customer_dashboard')")
    assert response.resolver_match.view_name == 'customer_dashboard', "Dashboard redirect did not route customer correctly"
    
    # My Cars page
    response = c.get(reverse('my_cars'))
    print(f"  GET reverse('my_cars'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "My Cars page failed to load"
    
    # Request Service page
    response = c.get(reverse('request_service'))
    print(f"  GET reverse('request_service'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Request Service page failed to load"
    
    # Service Status page
    response = c.get(reverse('service_status'))
    print(f"  GET reverse('service_status'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Service Status page failed to load"
    
    # Profile page
    response = c.get(reverse('profile'))
    print(f"  GET reverse('profile'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Profile page failed to load"

    # Log out customer
    c.logout()


    # 3. Admin Authentication & Views
    print("\n[3] Testing Admin Authentication & Views:")
    
    # Log in Admin
    login_success = c.login(username='admin@csms.com', password='adminpassword')
    print(f"  Login admin@csms.com: Result = {login_success} (Expected True)")
    assert login_success, "Admin login failed"
    
    # Redirect Dashboard
    response = c.get('/services/dashboard/', follow=True)
    print(f"  GET '/services/dashboard/' (Redirect check): Final Path = '{response.resolver_match.view_name}' (Expected 'admin_dashboard')")
    assert response.resolver_match.view_name == 'admin_dashboard', "Dashboard redirect did not route admin correctly"
    
    # Admin Customers page
    response = c.get(reverse('admin_customers'))
    print(f"  GET reverse('admin_customers'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Admin customers page failed to load"
    
    # Admin Cars page
    response = c.get(reverse('admin_cars'))
    print(f"  GET reverse('admin_cars'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Admin cars page failed to load"
    
    # Admin Service Requests page
    response = c.get(reverse('admin_service_requests'))
    print(f"  GET reverse('admin_service_requests'): Status Code = {response.status_code} (Expected 200)")
    assert response.status_code == 200, "Admin requests page failed to load"

    # Admin Update Status Page
    req = ServiceRequest.objects.first()
    if req:
        response = c.get(reverse('admin_update_status', kwargs={'request_id': req.id}))
        print(f"  GET reverse('admin_update_status', {req.id}): Status Code = {response.status_code} (Expected 200)")
        assert response.status_code == 200, "Admin update status page failed to load"
        
        # Post status update
        response = c.post(reverse('admin_update_status', kwargs={'request_id': req.id}), {'status': 'Completed'}, follow=True)
        req.refresh_from_db()
        print(f"  POST update status of request #{req.id} to 'Completed': Success. DB Status = '{req.status}' (Expected 'Completed')")
        assert req.status == 'Completed', "Admin status update post failed"

    c.logout()


    # 4. CRUD Car Operations
    print("\n[4] Testing Customer Car CRUD operations:")
    
    login_success = c.login(username='john@example.com', password='customerpassword')
    assert login_success
    
    # Clean up any leftover test car from previous runs
    Car.objects.filter(car_number='KA-01-CR-9999').delete()

    # Count cars before
    initial_cars_count = Car.objects.filter(user__username='john@example.com').count()
    
    # Create a new car
    new_car_num = 'KA-01-CR-9999'
    response = c.post(reverse('add_car'), {
        'car_brand': 'Audi',
        'car_model': 'R8',
        'car_number': new_car_num
    }, follow=True)
    
    new_cars_count = Car.objects.filter(user__username='john@example.com').count()
    print(f"  POST add new car (Audi R8, {new_car_num}): Count went from {initial_cars_count} to {new_cars_count} (Expected increase by 1)")
    assert new_cars_count == initial_cars_count + 1, "Car was not added to the database"
    
    # Edit the car
    added_car = Car.objects.get(car_number=new_car_num)
    response = c.post(reverse('edit_car', kwargs={'car_id': added_car.id}), {
        'car_brand': 'Audi',
        'car_model': 'R8 V10',
        'car_number': new_car_num
    }, follow=True)
    
    added_car.refresh_from_db()
    print(f"  POST edit car model to 'R8 V10': DB Model = '{added_car.car_model}' (Expected 'R8 V10')")
    assert added_car.car_model == 'R8 V10', "Car model was not updated"
    
    # Delete the car
    response = c.post(reverse('delete_car', kwargs={'car_id': added_car.id}), follow=True)
    post_delete_cars_count = Car.objects.filter(user__username='john@example.com').count()
    print(f"  POST delete car: Count went from {new_cars_count} to {post_delete_cars_count} (Expected decrease by 1)")
    assert post_delete_cars_count == initial_cars_count, "Car was not deleted from the database"

    c.logout()
    print("\n=================== ALL TESTS COMPLETED SUCCESSFULLY! ===================")

if __name__ == '__main__':
    run_tests()
