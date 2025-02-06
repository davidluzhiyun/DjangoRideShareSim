from django import forms
from rides.models.ride import Ride
from rides.models.ride_sharer import RideSharer
from django.utils import timezone

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            'destination', 
            'arrival_time', 
            'owner_party_size',
            'vehicle_type',
            'special_requests',
            'shareable'
        ]
        widgets = {
            'arrival_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'required': True},
                format='%Y-%m-%dT%H:%M'
            )
        }
    
    def clean_arrival_time(self):
        arrival_time = self.cleaned_data.get('arrival_time')
        if not arrival_time:
            raise forms.ValidationError("Arrival time is required")
        if arrival_time <= timezone.now():
            raise forms.ValidationError("Arrival time must be in the future")
        return arrival_time

class RideSearchForm(forms.Form):
    destination = forms.CharField(required=False)
    earliest_arrival = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    latest_arrival = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
    )
    party_size = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        earliest = cleaned_data.get('earliest_arrival')
        latest = cleaned_data.get('latest_arrival')
        
        if earliest and latest and earliest >= latest:
            raise forms.ValidationError(
                "Earliest arrival must be before latest arrival"
            )
        return cleaned_data

class RideSharerForm(forms.ModelForm):
    class Meta:
        model = RideSharer
        fields = ['party_size', 'earliest_arrival', 'latest_arrival']
        widgets = {
            'earliest_arrival': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'latest_arrival': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            )
        }

    def clean(self):
        cleaned_data = super().clean()
        earliest = cleaned_data.get('earliest_arrival')
        latest = cleaned_data.get('latest_arrival')
        if earliest and latest:
            if earliest >= latest:
                raise forms.ValidationError(
                    "Earliest arrival must be before latest arrival"
                )
            if earliest <= timezone.now():
                raise forms.ValidationError(
                    "Earliest arrival must be in the future"
                )
        return cleaned_data

class DriverSearchForm(forms.Form):
    vehicle_type = forms.CharField(required=False)
    max_passengers = forms.IntegerField(required=False)
    destination = forms.CharField(required=False)