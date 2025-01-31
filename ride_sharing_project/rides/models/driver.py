from ride_sharing_project.rides import models


class Vehicle(models.Model):
    driver = models.OneToOneField(
        models.User,
        on_delete=models.CASCADE,
        related_name='vehicle',
        help_text='User who drives this vehicle'
    )
    vehicle_type = models.CharField(
        max_length=100,
        help_text='Type of vehicle'
    )
    license_plate = models.CharField(
        max_length=25,
        unique=True,
        help_text='Vehicle license plate number'
    )
    max_passengers = models.PositiveIntegerField(
        help_text='Maximum number of passengers the vehicle can accommodate'
    )
    special_info = models.TextField(
        blank=True,
        help_text='Any special vehicle information'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_accommodate_ride(self, ride):
        "Check if vehicle can accommodate the ride"
        return (
            self.max_passengers >= ride.total_passengers and
            (not ride.vehicle_type or ride.vehicle_type.lower() == self.vehicle_type.lower()) and
            (not ride.special_requests or ride.special_requests == self.special_info)
        )
