from django.contrib import admin
from .models import User, Vehicle, Ride, RideSharer

admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(Ride)
admin.site.register(RideSharer)