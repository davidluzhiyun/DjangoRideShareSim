from django.urls import path
from rides.views import ride_views

app_name = 'rides'

urlpatterns = [
    path('', ride_views.ride_list, name='list'),
    path('request/', ride_views.request_ride, name='request'),
    path('<int:ride_id>/', ride_views.ride_detail, name='detail'),
    path('<int:ride_id>/edit/', ride_views.edit_ride, name='edit'),
    path('search/', ride_views.search_sharable_rides, name='search'),
    path('<int:ride_id>/join/', ride_views.join_ride, name='join'),
    path('my-rides/', ride_views.my_rides, name='my_rides'),
]