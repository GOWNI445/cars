import os
import shutil
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_service_project.settings')
django.setup()

from django.test import Client
from accounts.models import User
from seed_db import seed

# Ensure database is seeded with demo data
seed()

dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
if os.path.exists(dist_dir):
    shutil.rmtree(dist_dir)
os.makedirs(dist_dir, exist_ok=True)

# Copy static assets (css, images) to docs/static/
static_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
static_dst = os.path.join(dist_dir, 'static')
shutil.copytree(static_src, static_dst)

client = Client()

# Map of internal URLs to static filenames and auth requirements
pages = [
    ('/', 'index.html', None),
    ('/login/', 'login.html', None),
    ('/register/', 'register.html', None),
    ('/services/dashboard/customer/', 'customer_dashboard.html', 'john@example.com'),
    ('/cars/', 'my_cars.html', 'john@example.com'),
    ('/services/request/', 'request_service.html', 'john@example.com'),
    ('/services/status/', 'service_status.html', 'john@example.com'),
    ('/profile/', 'profile.html', 'john@example.com'),
    ('/services/dashboard/admin/', 'admin_dashboard.html', 'admin@csms.com'),
    ('/services/admin/customers/', 'admin_customers.html', 'admin@csms.com'),
    ('/services/admin/cars/', 'admin_cars.html', 'admin@csms.com'),
    ('/services/admin/requests/', 'admin_service_requests.html', 'admin@csms.com'),
]

url_map = [
    (r'href=["\']/(?:home)?["\']', 'href="index.html"'),
    (r'href=["\']/login/["\']', 'href="login.html"'),
    (r'href=["\']/register/["\']', 'href="register.html"'),
    (r'href=["\']/logout/["\']', 'href="index.html"'),
    (r'href=["\']/services/dashboard/customer/["\']', 'href="customer_dashboard.html"'),
    (r'href=["\']/services/dashboard/admin/["\']', 'href="admin_dashboard.html"'),
    (r'href=["\']/services/dashboard/["\']', 'href="customer_dashboard.html"'),
    (r'href=["\']/cars/["\']', 'href="my_cars.html"'),
    (r'href=["\']/services/request/["\']', 'href="request_service.html"'),
    (r'href=["\']/services/status/["\']', 'href="service_status.html"'),
    (r'href=["\']/profile/["\']', 'href="profile.html"'),
    (r'href=["\']/services/admin/customers/["\']', 'href="admin_customers.html"'),
    (r'href=["\']/services/admin/cars/["\']', 'href="admin_cars.html"'),
    (r'href=["\']/services/admin/requests/["\']', 'href="admin_service_requests.html"'),
    (r'href=["\']/static/', 'href="static/'),
    (r'src=["\']/static/', 'src="static/'),
]

for url, filename, auth_user in pages:
    client.logout()
    if auth_user:
        if auth_user == 'admin@csms.com':
            client.login(username=auth_user, password='adminpassword')
        else:
            client.login(username=auth_user, password='customerpassword')
    
    resp = client.get(url)
    if resp.status_code == 200:
        html = resp.content.decode('utf-8')
        for pattern, replacement in url_map:
            html = re.sub(pattern, replacement, html)
        
        # Write to docs/
        out_path = os.path.join(dist_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated {filename} from {url}")
    else:
        print(f"Failed {url} with status {resp.status_code}")

print("Static site generation completed in 'docs/' directory!")
