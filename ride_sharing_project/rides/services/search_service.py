# rides/services/search_service.py
from urllib import request
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from ride_sharing_project.rides.forms.ride_forms import RideSearchForm
from ..models.ride import Ride, RideStatus

class SearchService:
    """
    Service class to handle all search-related functionality
    """
    
    def search_sharable_rides(self, filters):
        form = RideSearchForm(request.GET)
        rides = []
        search_performed = bool(request.GET)
    
        if form.is_valid():
            earliest = form.cleaned_data['earliest_arrival']
            latest = form.cleaned_data['latest_arrival']
            party_size = form.cleaned_data['party_size']
            destination = form.cleaned_data.get('destination', '')
            
            rides = Ride.objects.filter(
            status=RideStatus.OPEN,
            shareable=True,
            arrival_time__gte=earliest,
            arrival_time__lte=latest
        ).exclude(owner=request.user)
        
        if destination:
            rides = rides.filter(destination__icontains=destination)
            
        # Filter rides that can accommodate the party size:
        rides = [
            ride for ride in rides 
            if not ride.driver or (ride.total_passengers + party_size) <= ride.driver.max_passengers
        ]

        context = {
        'form': form,
        'rides': rides,
        'search_performed': search_performed
        }
        return render(request, 'rides/ride/search.html', context)

    def search_available_rides_for_driver(self, vehicle):
        """
        Search for rides that a driver with given vehicle can serve
        """
        rides = Ride.objects.filter(
            status=RideStatus.OPEN,
            arrival_time__gt=timezone.now()
        )

        # Filter by vehicle capacity
        rides = rides.filter(
            Q(vehicle_type='') | Q(vehicle_type__iexact=vehicle.vehicle_type)
        )

        # Filter by special requirements
        if vehicle.special_info:
            rides = rides.filter(
                Q(special_requests='') | Q(special_requests=vehicle.special_info)
            )

        # Filter out rides that exceed vehicle capacity
        return [
            ride for ride in rides
            if ride.total_passengers <= vehicle.max_passengers
        ]

    def search_rides_by_status(self, user, status=None):
        """
        Search for rides associated with a user by status
        """
        owned_rides = user.owned_rides.all()
        shared_rides = user.shared_rides.all()
        
        if hasattr(user, 'vehicle'):
            driven_rides = user.vehicle.driven_rides.all()
        else:
            driven_rides = Ride.objects.none()

        if status:
            owned_rides = owned_rides.filter(status=status)
            shared_rides = shared_rides.filter(ride__status=status)
            driven_rides = driven_rides.filter(status=status)

        return {
            'owned': owned_rides,
            'shared': shared_rides,
            'driven': driven_rides
        }