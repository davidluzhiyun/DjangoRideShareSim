from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms.auth_forms import UserRegistrationForm
#register user
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            #redirect to the rides list page
            return redirect('rides:list')
    else:
        form = UserRegistrationForm()
    #display the registration form for the user to fill
    return render(request, 'rides/auth/register.html', {'form': form})
#view profile, login required by the user to view profile
@login_required
def profile(request):
    context = {
        'owned_rides': request.user.owned_rides.all(),
        'shared_rides': request.user.shared_rides.all(),
        'is_driver': hasattr(request.user, 'vehicle')
    }
    #display the user profile after loggin in
    return render(request, 'rides/auth/profile.html', context)