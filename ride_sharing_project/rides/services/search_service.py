# rides/services/search_service.py
from django.db.models import Q
from django.utils import timezone
from ..models.ride import Ride, RideStatus

class SearchService:
    """
    Service class to handle all search-related functionality
    """
    
    def search_sharable_rides(self, filters):
        """
        Search for sharable rides based on destination and arrival window
        """
        rides = Ride.objects.filter(
            status=RideStatus.OPEN,
            shareable=True
        )

        # Filter by destination if provided
        if filters.get('destination'):
            rides = rides.filter(
                destination__icontains=filters['destination']
            )

        # Filter by arrival window
        if filters.get('earliest_arrival') and filters.get('latest_arrival'):
            rides = rides.filter(
                arrival_time__gte=filters['earliest_arrival'],
                arrival_time__lte=filters['latest_arrival']
            )

        # Exclude rides that would exceed capacity with new passengers
        if filters.get('party_size'):
            rides = [
                ride for ride in rides
                if not ride.driver or  # No driver assigned yet
                ride.total_passengers + filters['party_size'] <= ride.driver.max_passengers
            ]

        return rides

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