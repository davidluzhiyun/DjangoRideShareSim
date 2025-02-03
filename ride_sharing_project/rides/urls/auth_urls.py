from django.urls import path
from django.contrib.auth import views as auth_views
from rides.views import auth_views as custom_auth_views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='rides/auth/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        template_name='rides/auth/logged_out.html',  # Add template
        next_page='accounts:login',  # Redirect to login after logout
        http_method_names=['get', 'post']  # Allow both GET and POST
    ), name='logout'),
    
    path('register/', custom_auth_views.register, name='register'),
]