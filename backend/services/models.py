from django.db import models
from django.conf import settings
from cars.models import Car

class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='service_requests')
    service_type = models.CharField(max_length=255)
    request_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    admin_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Request #{self.id} - {self.car} - {self.status}"
