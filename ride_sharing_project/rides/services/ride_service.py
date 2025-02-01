# rides/services/ride_service.py
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models.ride import Ride, RideStatus
from ..models.ride_sharer import RideSharer
from .email_service import EmailService

class RideService:
    """
    Service class to handle ride-related business logic
    """
    def __init__(self):
        self.email_service = EmailService()

    @transaction.atomic
    def create_ride(self, owner, data):
        """Create a new ride request"""
        if data['arrival_time'] <= timezone.now():
            raise ValidationError("Arrival time must be in the future")

        ride = Ride.objects.create(
            owner=owner,
            destination=data['destination'],
            arrival_time=data['arrival_time'],
            owner_party_size=data['owner_party_size'],
            vehicle_type=data.get('vehicle_type', ''),
            special_requests=data.get('special_requests', ''),
            shareable=data.get('shareable', False)
        )
        return ride

    @transaction.atomic
    def update_ride(self, ride, data):
        """Update an existing ride"""
        if not ride.is_modifiable:
            raise ValidationError("Cannot modify a confirmed or completed ride")

        for field, value in data.items():
            setattr(ride, field, value)
        ride.save()
        return ride

    @transaction.atomic
    def add_sharer(self, ride, user, data):
        """Add a sharer to a ride"""
        if not ride.shareable:
            raise ValidationError("This ride is not shareable")
        
        if ride.status != RideStatus.OPEN:
            raise ValidationError("Can only join open rides")
        
        if RideSharer.objects.filter(ride=ride, user=user).exists():
            raise ValidationError("Already sharing this ride")

        # Validate arrival window
        if not (data['earliest_arrival'] <= ride.arrival_time <= data['latest_arrival']):
            raise ValidationError("Ride arrival time is outside acceptable window")

        sharer = RideSharer.objects.create(
            ride=ride,
            user=user,
            party_size=data['party_size'],
            earliest_arrival=data['earliest_arrival'],
            latest_arrival=data['latest_arrival']
        )
        return sharer

    @transaction.atomic
    def confirm_ride(self, ride, vehicle):
        """Confirm a ride with a driver"""
        if ride.status != RideStatus.OPEN:
            raise ValidationError("Only open rides can be confirmed")

        # Check vehicle capacity
        if ride.total_passengers > vehicle.max_passengers:
            raise ValidationError("Vehicle cannot accommodate all passengers")

        # Check vehicle type if specified
        if ride.vehicle_type and ride.vehicle_type.lower() != vehicle.vehicle_type.lower():
            raise ValidationError("Vehicle type does not match requirements")

        # Check special requests if specified
        if ride.special_requests and ride.special_requests != vehicle.special_info:
            raise ValidationError("Vehicle does not meet special requirements")

        ride.driver = vehicle
        ride.status = RideStatus.CONFIRMED
        ride.save()

        # Send confirmation emails
        self._notify_ride_confirmation(ride)
        return ride

    @transaction.atomic
    def complete_ride(self, ride):
        """Mark a ride as complete"""
        if ride.status != RideStatus.CONFIRMED:
            raise ValidationError("Only confirmed rides can be completed")

        ride.status = RideStatus.COMPLETE
        ride.save()
        return ride

    def get_user_rides(self, user):
        """Get all rides associated with a user"""
        return {
            'owned': {
                'open': user.owned_rides.filter(status=RideStatus.OPEN),
                'confirmed': user.owned_rides.filter(status=RideStatus.CONFIRMED),
                'completed': user.owned_rides.filter(status=RideStatus.COMPLETE)
            },
            'shared': RideSharer.objects.filter(user=user).select_related('ride'),
            'driven': user.vehicle.driven_rides.all() if hasattr(user, 'vehicle') else None
        }

    def _notify_ride_confirmation(self, ride):
        """Send confirmation notifications to all ride participants"""
        participants = [ride.owner]
        sharers = ride.sharers.select_related('user')
        participants.extend([sharer.user for sharer in sharers])
        
        for participant in participants:
            self.email_service.send_ride_confirmation(
                user=participant,
                ride=ride
            )