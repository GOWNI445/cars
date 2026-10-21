# 🚗 Car Service Management System (CSMS)

A full-stack auto repair and maintenance management portal built with **Python Django** and **MySQL**, styled with a dark glassmorphic UI.

---

## ✨ Features

- **Customer Portal**:
  - Register and manage multiple vehicles with dynamic 3D mockup graphics.
  - Schedule service appointments (Oil change, Tyre replacement, Engine repair, etc.).
  - Real-time service tracking (Pending, In Progress, Completed, Cancelled).
  - Filter requests by car brand and sort by newest/oldest records.
  
- **Admin Command Desk**:
  - Comprehensive dashboard with system metrics, vehicle counts, and request stats.
  - Granular customer directory with vehicle counts and contact details.
  - Inline service status management with custom admin notes.
  - Vehicle management (Edit/Delete customer cars directly).
  - Secure role-based view restrictions.

- **Email Notifications**:
  - Automated status update notifications delivered to customer email addresses.
  - Embedded administrator messages and service notes.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.14, Django 6.0
- **Database**: MySQL
- **Frontend**: Django Templates, HTML5, CSS3 (Vanilla Glassmorphic Design)

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- MySQL Server

### 2. Setup & Installation
```bash
# Clone the repository
git clone https://github.com/GOWNI445/car-service-management-system.git
cd car-service-management-system

# Install Python dependencies
pip install django mysqlclient
```

### 3. Database Configuration
Update database credentials in `backend/car_service_project/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'csms',
        'USER': 'root',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Run Migrations & Seed Demo Data
```bash
python backend/manage.py migrate
python backend/seed_db.py
```

### 5. Start the Server
```bash
python backend/manage.py runserver
# or using npm
npm run server
```
Open **http://127.0.0.1:8000/** in your browser.

---

## 👤 Default Demo Credentials

- **Admin Account**:
  - **Username / Email**: `admin@csms.com`
  - **Password**: `adminpassword`
- **Customer Account**:
  - **Username / Email**: `john@example.com`
  - **Password**: `customerpassword`
