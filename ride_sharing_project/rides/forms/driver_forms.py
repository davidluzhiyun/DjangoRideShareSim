from django import forms
from rides.models.driver import Vehicle

class DriverRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'license_plate', 'max_passengers', 'special_info']
        
    def clean_license_plate(self):
        license_plate = self.cleaned_data.get('license_plate')
        if Vehicle.objects.filter(license_plate=license_plate).exists():
            raise forms.ValidationError("This license plate is already registered.")
        return license_plate
