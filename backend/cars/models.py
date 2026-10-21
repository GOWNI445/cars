from django.db import models
from django.conf import settings

class Car(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cars')
    car_brand = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_number = models.CharField(max_length=50)

    @property
    def car_image_url(self):
        brand = self.car_brand.lower().strip()
        model = self.car_model.lower().strip()
        
        if 'tesla' in brand or 'tesla' in model:
            return 'images/tesla.jpg'
        if 'bmw' in brand or 'bmw' in model:
            return 'images/bmw.jpg'
        if 'toyota' in brand or 'toyota' in model or 'supra' in model:
            return 'images/toyota.jpg'
        if 'audi' in brand or 'audi' in model or 'r8' in model:
            return 'images/audi.jpg'
        if 'honda' in brand or 'honda' in model or 'civic' in model:
            return 'images/honda.jpg'
        if 'ford' in brand or 'ford' in model or 'mustang' in model:
            return 'images/ford.jpg'
        if 'mercedes' in brand or 'benz' in brand or 'mercedes' in model:
            return 'images/mercedes.jpg'
        if 'skoda' in brand or 'skoda' in model or 'scoda' in brand or 'scoda' in model:
            return 'images/skoda.jpg'
            
        # Fallback pool based on car ID to ensure different cars get different images
        image_pool = [
            'images/generic.jpg',
            'images/tesla.jpg',
            'images/bmw.jpg',
            'images/toyota.jpg',
            'images/audi.jpg',
            'images/honda.jpg',
            'images/ford.jpg',
            'images/mercedes.jpg',
            'images/skoda.jpg'
        ]
        pool_index = (self.id or 0) % len(image_pool)
        return image_pool[pool_index]

    def __str__(self):
        return f"{self.car_brand} {self.car_model} ({self.car_number})"
