from django import forms
from django.contrib.auth import get_user_model
from ..models import Vehicle

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class VehicleProfileForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_passengers', 'special_info']