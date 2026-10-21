import os
import django

# Set up django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_service_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from cars.models import Car
from services.models import ServiceRequest
from datetime import date, timedelta

User = get_user_model()

def seed():
    print("Seeding database...")
    
    # 1. Create admin user
    admin_email = 'admin@csms.com'
    if not User.objects.filter(email=admin_email).exists():
        admin = User.objects.create_superuser(
            username=admin_email,
            email=admin_email,
            password='adminpassword',
            name='System Admin',
            role='admin'
        )
        print("Created Admin User:", admin_email)
    else:
        print("Admin User already exists.")

    # 2. Create customer John
    john_email = 'john@example.com'
    if not User.objects.filter(username=john_email).exists():
        john = User.objects.create_user(
            username=john_email,
            email=john_email,
            password='customerpassword',
            name='John Doe',
            phone='1234567890',
            role='customer'
        )
        print("Created Customer:", john_email)
    else:
        john = User.objects.get(username=john_email)
        john.role = 'customer'
        john.email = john_email
        john.save()
        print("Customer already exists (role reset to customer):", john_email)

    # 3. Create customer Jane
    jane_email = 'jane@example.com'
    if not User.objects.filter(username=jane_email).exists():
        jane = User.objects.create_user(
            username=jane_email,
            email=jane_email,
            password='customerpassword',
            name='Jane Smith',
            phone='9876543210',
            role='customer'
        )
        print("Created Customer:", jane_email)
    else:
        jane = User.objects.get(username=jane_email)
        jane.role = 'customer'
        jane.email = jane_email
        jane.save()
        print("Customer already exists (role reset to customer):", jane_email)

    # 4. Create cars for John
    car1_num = 'KA-01-MJ-5678'
    if not Car.objects.filter(car_number=car1_num).exists():
        car1 = Car.objects.create(
            user=john,
            car_brand='Tesla',
            car_model='Model S',
            car_number=car1_num
        )
        print("Created Car for John:", car1)
    else:
        car1 = Car.objects.get(car_number=car1_num)

    car2_num = 'KA-01-AB-1234'
    if not Car.objects.filter(car_number=car2_num).exists():
        car2 = Car.objects.create(
            user=john,
            car_brand='BMW',
            car_model='M3',
            car_number=car2_num
        )
        print("Created Car for John:", car2)
    else:
        car2 = Car.objects.get(car_number=car2_num)

    # 5. Create car for Jane
    car3_num = 'MH-02-XY-9876'
    if not Car.objects.filter(car_number=car3_num).exists():
        car3 = Car.objects.create(
            user=jane,
            car_brand='Toyota',
            car_model='Supra',
            car_number=car3_num
        )
        print("Created Car for Jane:", car3)
    else:
        car3 = Car.objects.get(car_number=car3_num)

    # 6. Create service requests
    # Pending request for John's Tesla
    if not ServiceRequest.objects.filter(car=car1, service_type='Battery Health Check').exists():
        req1 = ServiceRequest.objects.create(
            user=john,
            car=car1,
            service_type='Battery Health Check',
            request_date=date.today(),
            status='Pending'
        )
        print("Created Service Request:", req1)

    # In Progress request for John's BMW
    if not ServiceRequest.objects.filter(car=car2, service_type='Brake Pads Replacement').exists():
        req2 = ServiceRequest.objects.create(
            user=john,
            car=car2,
            service_type='Brake Pads Replacement',
            request_date=date.today() - timedelta(days=2),
            status='In Progress'
        )
        print("Created Service Request:", req2)

    # Completed request for Jane's Toyota
    if not ServiceRequest.objects.filter(car=car3, service_type='Regular Maintenance & Oil Change').exists():
        req3 = ServiceRequest.objects.create(
            user=jane,
            car=car3,
            service_type='Regular Maintenance & Oil Change',
            request_date=date.today() - timedelta(days=5),
            status='Completed'
        )
        print("Created Service Request:", req3)

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
