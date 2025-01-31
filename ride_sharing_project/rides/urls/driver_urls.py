from django.urls import path
from rides.views import driver_views

app_name = 'driver'

urlpatterns = [
    path('register/', driver_views.driver_register, name='register'),
    path('profile/', driver_views.driver_profile, name='profile'),
    path('search/', driver_views.search_rides, name='search_rides'),
    path('rides/', driver_views.driver_rides, name='my_rides'),
    path('ride/<int:ride_id>/accept/', driver_views.accept_ride, name='accept_ride'),
    path('ride/<int:ride_id>/complete/', driver_views.complete_ride, name='complete_ride'),
]