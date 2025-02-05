from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied
from ..models.ride import Ride, RideStatus
from ..models.ride_sharer import RideSharer
from ..forms.ride_forms import RideRequestForm, RideSearchForm, RideSharerForm
from ..services.ride_service import RideService
#list all the rides for the logged in user
@login_required
def ride_list(request):
    owned_rides = request.user.owned_rides.all()
    shared_rides = request.user.shared_rides.all()
    if hasattr(request.user, 'vehicle'):
        driven_rides = request.user.vehicle.driven_rides.all()
    else:
        driven_rides = []
    
    context = {
        'owned_rides': owned_rides,
        'shared_rides': shared_rides,
        'driven_rides': driven_rides
    }
    return render(request, 'rides/ride/list.html', context)
#create a new ride request
@login_required
def request_ride(request):
    """Create a new ride request."""
    if request.method == 'POST':
        form = RideRequestForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.owner = request.user
            ride.save()
            messages.success(request, 'Ride requested successfully!')
            return redirect('rides:detail', ride_id=ride.id)
    else:
        form = RideRequestForm()
    
    return render(request, 'rides/ride/request.html', {'form': form})
#view ride details
@login_required
def ride_detail(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    if not (ride.owner == request.user or
            ride.sharers.filter(user=request.user).exists() or
            (hasattr(request.user, 'vehicle') and ride.driver == request.user.vehicle)):
        raise PermissionDenied
    
    context = {
        'ride': ride,
        'is_owner': ride.owner == request.user,
        'is_sharer': ride.sharers.filter(user=request.user).exists(),
        'is_driver': hasattr(request.user, 'vehicle') and ride.driver == request.user.vehicle
    }
    return render(request, 'rides/ride/detail.html', context)
#edit the ride request
@login_required
def edit_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, owner=request.user)
    
    if not ride.is_modifiable:
        messages.error(request, 'Cannot modify a confirmed or completed ride.')
        return redirect('rides:detail', ride_id=ride.id)
    
    if request.method == 'POST':
        form = RideRequestForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ride updated successfully!')
            return redirect('rides:detail', ride_id=ride.id)
    else:
        form = RideRequestForm(instance=ride)
    
    return render(request, 'rides/ride/edit.html', {'form': form, 'ride': ride})
#search for rides that are available by matching the vehicle and the ride request
@login_required 
def search_sharable_rides(request):
    form = RideSearchForm(request.GET)
    rides = []
    search_performed = bool(request.GET)
    
    if form.is_valid():
        earliest = form.cleaned_data['earliest_arrival']
        latest = form.cleaned_data['latest_arrival']
        party_size = form.cleaned_data['party_size']
        destination = form.cleaned_data.get('destination', '')
        
        rides = Ride.objects.filter(
            status=RideStatus.OPEN,
            shareable=True,
            arrival_time__gte=earliest,
            arrival_time__lte=latest
        ).exclude(owner=request.user)
        
        if destination:
            rides = rides.filter(destination__icontains=destination)
            
        # Filter rides that can accommodate the party size
        rides = [
            ride for ride in rides 
            if not ride.driver or 
            ride.driver.can_accommodate_ride(ride.total_passengers + party_size)
        ]

    context = {
        'form': form,
        'rides': rides,
        'search_performed': search_performed
    }
    return render(request, 'rides/ride/search.html', context)
#join a ride that is shareable
@login_required
@transaction.atomic
def join_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, status=RideStatus.OPEN, shareable=True)
    
    if request.method == 'POST':
        form = RideSharerForm(request.POST)
        
        # Set ride and user before validation
        sharer = form.instance
        sharer.ride = ride
        sharer.user = request.user
        
        if form.is_valid():
            try:
                # Validate form data
                if sharer.party_size <= 0:
                    messages.error(request, "Party size must be greater than 0")
                elif sharer.earliest_arrival > sharer.latest_arrival:
                    messages.error(request, "Earliest arrival must be before latest arrival")
                elif ride.arrival_time < sharer.earliest_arrival or \
                     ride.arrival_time > sharer.latest_arrival:
                    messages.error(request, "Ride arrival time is outside acceptable window")
                else:
                    sharer.save()
                    messages.success(request, 'Successfully joined the ride!')
                    return redirect('rides:detail', ride_id=ride.id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RideSharerForm(initial={
            'earliest_arrival': ride.arrival_time,
            'latest_arrival': ride.arrival_time
        })
    
    return render(request, 'rides/ride/join.html', {
        'form': form,
        'ride': ride
    })
#display all the rides for the logged in user 
@login_required
def my_rides(request):
    context = {
        'owned_rides': request.user.owned_rides.all().order_by('-created_at'),
        'shared_rides': request.user.shared_rides.all().order_by('-created_at'),
    }
    if hasattr(request.user, 'vehicle'):
        context['driven_rides'] = request.user.vehicle.driven_rides.all().order_by('-created_at')
    
    return render(request, 'rides/ride/my_rides.html', context)