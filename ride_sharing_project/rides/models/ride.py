from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()

class RideStatus:
    OPEN = 'OPEN'
    CONFIRMED = 'CONFIRMED'
    COMPLETE = 'COMPLETE'
    
    CHOICES = [
        (OPEN, 'Open'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETE, 'Complete')
    ]

class Ride(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_rides',
        help_text='User who requested this ride'
    )
    destination = models.CharField(
        max_length=255,
        help_text='Destination address for the ride'
    )
    arrival_time = models.DateTimeField(
        help_text='Required arrival date and time'
    )
    owner_party_size = models.PositiveIntegerField(
        help_text='Number of passengers in owner\'s party'
    )    
    vehicle_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Preferred vehicle type (optional)'
    )
    special_requests = models.TextField(
        blank=True,
        help_text='Any special requests for the ride'
    )
    shareable = models.BooleanField(
        default=False,
        help_text='Whether this ride can be joined by other users'
    )
    status = models.CharField(
        max_length=10,
        choices=RideStatus.CHOICES,
        default=RideStatus.OPEN,
        help_text='Current status of the ride'
    )
    driver = models.ForeignKey(
        'Vehicle',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='driven_rides',
        help_text='Driver assigned to this ride'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'arrival_time']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['destination']),
        ]

    def clean(self):
        if self.arrival_time <= timezone.now():
            raise ValidationError("Arrival time must be in the future")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_modifiable(self):
        "Check if ride can still be modified"
        return self.status == RideStatus.OPEN

    @property
    def total_passengers(self):
        "Calculate the total number of passengers, including all sharers"
        sharer_count = self.sharers.aggregate(
            total=models.Sum('party_size'))['total'] or 0
        return self.owner_party_size + sharer_count
