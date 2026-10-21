from django import forms
from .models import ServiceRequest
from cars.models import Car

from datetime import date

class ServiceRequestForm(forms.ModelForm):
    SERVICE_TYPE_CHOICES = (
        ('Oil Change', 'Oil Change'),
        ('Tyre Replacement', 'Tyre Replacement'),
        ('General Checkup', 'General Checkup'),
        ('Engine Repair', 'Engine Repair'),
        ('Other', 'Other'),
    )

    service_type = forms.ChoiceField(choices=SERVICE_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = ServiceRequest
        fields = ['car', 'service_type', 'request_date', 'notes']
        widgets = {
            'request_date': forms.DateInput(attrs={'type': 'date', 'min': '2026-08-01', 'max': '2026-08-31'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Enter optional notes/comments (e.g. issues faced)...', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Make date selection optional
        self.fields['request_date'].required = False
        if user:
            # Only show cars belonging to the current user
            self.fields['car'].queryset = Car.objects.filter(user=user)
            self.fields['car'].empty_label = "Select a Car"

    def clean_request_date(self):
        request_date = self.cleaned_data.get('request_date')
        if request_date:
            if request_date.year != 2026 or request_date.month != 8:
                raise forms.ValidationError("You can only request services for the month of August 2026.")
        return request_date


class ServiceStatusUpdateForm(forms.ModelForm):
    admin_message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter optional message to send to the customer (e.g. accepted details, reason for rejection)...', 'rows': 4}),
        required=False,
        label="Message to Customer"
    )
    class Meta:
        model = ServiceRequest
        fields = ['status', 'admin_message']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
