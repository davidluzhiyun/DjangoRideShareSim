from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms.profile_forms import UserProfileForm, VehicleProfileForm

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        vehicle_form = VehicleProfileForm(request.POST, instance=getattr(request.user, 'vehicle', None))
        
        if user_form.is_valid() and (not hasattr(request.user, 'vehicle') or vehicle_form.is_valid()):
            user_form.save()
            if hasattr(request.user, 'vehicle') and vehicle_form.has_changed():
                vehicle = vehicle_form.save(commit=False)
                vehicle.driver = request.user
                vehicle.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('rides:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        vehicle_form = VehicleProfileForm(instance=getattr(request.user, 'vehicle', None))
    
    return render(request, 'rides/profile/edit.html', {
        'user_form': user_form,
        'vehicle_form': vehicle_form
    })