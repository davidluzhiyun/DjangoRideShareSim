from django.forms import ValidationError
from ride_sharing_project.rides import models
from ride_sharing_project.rides.models.ride import Ride, RideStatus


class RideSharer(models.Model):
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='sharers',
        help_text='Ride being shared'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_rides',
        help_text='User sharing the ride'
    )
    party_size = models.PositiveIntegerField(
        help_text='Number of passengers in sharer\'s party'
    )
    earliest_arrival = models.DateTimeField(
        help_text='Earliest acceptable arrival time'
    )
    latest_arrival = models.DateTimeField(
        help_text='Latest acceptable arrival time'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['ride', 'user']
        indexes = [
            models.Index(fields=['earliest_arrival', 'latest_arrival']),
        ]
# adding validation error msg for earliest arrival time, latest arrival time, ride status, and ride arrival time
    def clean(self):
        if self.earliest_arrival > self.latest_arrival:
            raise ValidationError("Earliest arrival must be before latest arrival")
        if not self.ride.shareable:
            raise ValidationError("This ride is not shareable")
        if self.ride.arrival_time < self.earliest_arrival or \
           self.ride.arrival_time > self.latest_arrival:
            raise ValidationError("Ride arrival time is outside acceptable window")
        if self.ride.status != RideStatus.OPEN:
            raise ValidationError("Can only join open rides")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)