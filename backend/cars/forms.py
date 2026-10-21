from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['car_brand', 'car_model', 'car_number']
        widgets = {
            'car_brand': forms.TextInput(attrs={'placeholder': 'e.g. Toyota, Honda'}),
            'car_model': forms.TextInput(attrs={'placeholder': 'e.g. Camry, Civic'}),
            'car_number': forms.TextInput(attrs={'placeholder': 'e.g. KA-01-AB-1234'}),
        }

    def clean_car_number(self):
        return self.cleaned_data.get('car_number').strip().upper()
