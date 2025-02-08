from django.urls import path
from django.contrib.auth import views as auth_views
from rides.views import auth_views as custom_auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='rides/auth/login.html',
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        template_name='rides/auth/logged_out.html',
        next_page='accounts:login',  
        http_method_names=['get', 'post'],
    ), name='logout'),
    
    path('register/', custom_auth_views.register, name='register'),
]