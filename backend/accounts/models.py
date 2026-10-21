from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    first_name = None
    last_name = None
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.role})"
