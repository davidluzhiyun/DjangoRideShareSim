from django.shortcuts import redirect
from django.urls import reverse

def index_redirect(request):
    if request.user.is_authenticated:
        return redirect(reverse('rides:list'))
    else:
        return redirect(reverse('accounts:login'))