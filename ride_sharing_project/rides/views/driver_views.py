from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..forms.driver_forms import DriverRegistrationForm
from ..models.ride import Ride, RideStatus
from ..models.vehicle import Vehicle
from ..services.ride_service import RideService
from ..forms.ride_forms import DriverSearchForm

#register user as a driver , login is required by the user to register as a driver
@login_required
def driver_register(request):
    if hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You are already registered as a driver.')
        return redirect('driver:profile')
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user
            vehicle.save()
            messages.success(request, 'Successfully registered as a driver!')
            return redirect('driver:profile')
    else:
        form = DriverRegistrationForm()
    
    return render(request, 'rides/driver/register.html', {'form': form})

#display the driver profile and give option to edit profile details 
@login_required
def driver_profile(request):
    if not hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You need to register as a driver first.')
        return redirect('driver:register')
    
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, instance=request.user.vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('driver:profile')
    else:
        form = DriverRegistrationForm(instance=request.user.vehicle)
    
    context = {
        'form': form,
        'active_rides': request.user.vehicle.driven_rides.exclude(
            status=RideStatus.COMPLETE
        )
    }
    return render(request, 'rides/driver/profile.html', context)
#search for rides that are available by matching the vehicle 
@login_required
def search_rides(request):
    if not hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You need to register as a driver first.')
        return redirect('driver:register')
    
    form = DriverSearchForm(request.GET)
    rides = []
    
    if form.is_valid():
        rides = Ride.objects.filter(
            status=RideStatus.OPEN
        ).select_related('owner')
        
        vehicle = request.user.vehicle
        rides = [
            ride for ride in rides
            if vehicle.can_accommodate(ride.total_passengers) and
            vehicle.matches_requirements(
                ride.vehicle_type,
                ride.special_requests
            )
        ]
    #display the search form and the rides that are available
    context = {
        'form': form,
        'rides': rides,
    }
    #display froms in the drivers view page to serch for rides
    return render(request, 'rides/driver/search.html', context)
#display all the rides for the logged in driver
@login_required
def driver_rides(request):
    if not hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You need to register as a driver first.')
        return redirect('driver:register')
    
    rides = request.user.vehicle.driven_rides.all().order_by('-created_at')
    return render(request, 'rides/driver/rides.html', {'rides': rides})
#accept a ride request
@login_required
@transaction.atomic
def accept_ride(request, ride_id):
    if not hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You need to register as driver first.')
        return redirect('driver:register')
    
    ride = get_object_or_404(Ride, id=ride_id, status=RideStatus.OPEN)
    vehicle = request.user.vehicle
    #confirm the ride and show msg
    try:
        ride_service = RideService()
        ride_service.confirm_ride(ride, vehicle)
        messages.success(request, 'Ride accepted successfully!')
    except ValueError as e:
        messages.error(request, str(e))
    #redirect to the rides page for driver
    return redirect('driver:my_rides')
#completing a ride
@login_required
def complete_ride(request, ride_id):
    ride = get_object_or_404(
        Ride,
        id=ride_id,
        driver=request.user.vehicle,
        status=RideStatus.CONFIRMED
    )
    #complete the ride and display the message
    try:
        ride_service = RideService()
        ride_service.complete_ride(ride)
        messages.success(request, 'Ride completed!')
    #display err msg if any error occurs
    except ValueError as e:
        messages.error(request, str(e))
    #redirect to the driver rides page
    return redirect('driver:my_rides')