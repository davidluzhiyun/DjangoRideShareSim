from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from ..forms.driver_forms import DriverRegistrationForm as VehicleForm  # Changed import
from ..models.ride import Ride, RideStatus
from ..models.vehicle import Vehicle 
from ..services.ride_service import RideService
from ..forms.ride_forms import DriverSearchForm

#register user as a driver , login is required by the user to register as a driver
@login_required
def driver_profile(request):
    vehicle = getattr(request.user, 'vehicle', None)
    if not vehicle:
        return redirect('driver:register')
        
    form = VehicleForm(instance=vehicle)
    return render(request, 'rides/driver/profile.html', {'form': form, 'vehicle': vehicle})

@login_required
def driver_register(request):
    if hasattr(request.user, 'vehicle'):
        vehicle = request.user.vehicle
    else:
        vehicle = None
        
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user
            vehicle.save()
            messages.success(request, 'Vehicle information updated successfully!')
            return redirect('driver:profile')
    else:
        form = VehicleForm(instance=vehicle)
        
    return render(request, 'rides/driver/register.html', {'form': form})
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

    try:
        # Pre-validate capacity
        if ride.total_passengers > vehicle.max_passengers:
            messages.error(request, f"Your vehicle cannot accommodate {ride.total_passengers} passengers (max: {vehicle.max_passengers})")
            return redirect('driver:search_rides')

        # Pre-validate vehicle type if specified
        if ride.vehicle_type and ride.vehicle_type.lower() != vehicle.vehicle_type.lower():
            messages.error(request, "Your vehicle type doesn't match the requirements")
            return redirect('driver:search_rides')
            
        ride_service = RideService()
        ride_service.confirm_ride(ride, vehicle)
        messages.success(request, 'Ride accepted successfully!')
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, "An error occurred while accepting the ride")
    
    return redirect('driver:my_rides')
#completing a ride
@login_required
@transaction.atomic
def complete_ride(request, ride_id):
    if not hasattr(request.user, 'vehicle'):
        messages.warning(request, 'You need to register as driver first.')
        return redirect('driver:register')

    try:
        ride = get_object_or_404(
            Ride, 
            id=ride_id,
            driver=request.user.vehicle,
            status=RideStatus.CONFIRMED
        )

        ride.status = RideStatus.COMPLETE
        ride.save()
        messages.success(request, 'Ride marked as complete!')
    except Ride.DoesNotExist:
        messages.error(request, 'Ride not found or cannot be completed')
    except Exception as e:
        messages.error(request, str(e))
    
    return redirect('driver:my_rides')

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
            if vehicle.can_accommodate_ride(ride) and  # Changed from can_accommodate to can_accommodate_ride
            (not ride.vehicle_type or 
             ride.vehicle_type.lower() == vehicle.vehicle_type.lower())
        ]
    
    context = {
        'form': form,
        'rides': rides,
        'search_performed': bool(request.GET)
    }
    
    return render(request, 'rides/driver/search.html', context)