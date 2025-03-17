# ERSS-HWK1-AR791-ZL303

## Getting Started
sudo apt-get install docker.io docker-compose
Go to docker-deploy
chmod o+x runserver.sh
chmod o+x initserver.sh
sudo docker-compose up
(To nuke everything and restart
sudo docker-compose down -v
sudo docker image rm

sudo docker system prune -a (FYI: this will remove all your docker images and containers))

### Directory Structure

```
erss-hwk1-ar791-zl303
    ├── README.md
    ├── auth_flow.png
    ├── driver_operation_flow.png
    ├── driver_registration_flow.png
    ├── request_book_rides_flow.png
    ├── ride_sharing_project
    │   ├── manage.py
    │   ├── ride_sharing_project
    │   │   ├── __init__.py
    │   │   ├── asgi.py
    │   │   ├── settings.py
    │   │   ├── settings.py~
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   └── rides
    │       ├── __init__.py
    │       ├── apps.py
    │       ├── forms
    │       │   ├── __init__.py
    │       │   ├── auth_forms.py
    │       │   ├── driver_forms.py
    │       │   └── ride_forms.py
    │       ├── models
    │       │   ├── __init__.py
    │       │   ├── ride.py
    │       │   ├── ride_sharer.py
    │       │   ├── user.py
    │       │   └── vehicle.py
    │       ├── services
    │       │   ├── email_service.py
    │       │   ├── ride_service.py
    │       │   └── search_service.py
    │       ├── templates
    │       │   └── rides
    │       │       ├── auth
    │       │       │   ├── login.html
    │       │       │   └── register.html
    │       │       ├── base.html
    │       │       ├── driver
    │       │       │   ├── profile.html
    │       │       │   ├── register.html
    │       │       │   ├── rides.html
    │       │       │   └── search.html
    │       │       └── ride
    │       │           ├── list.html
    │       │           ├── request.html
    │       │           └── search.html
    │       ├── urls
    │       │   ├── __init__.py
    │       │   ├── auth_urls.py
    │       │   ├── driver_urls.py
    │       │   └── ride_urls.py
    │       └── views
    │           ├── __init__.py
    │           ├── auth_views.py
    │           ├── driver_views.py
    │           └── ride_views.py
    └── share_ride_flow.png
```
```
- /accounts/login/
- /accounts/logout/ 
- /accounts/register/

- /driver/register/
- /driver/profile/
- /driver/search/
- /driver/rides/
- /driver/ride/<ride_id>/accept/
- /driver/ride/<ride_id>/complete/

- /rides/ (list view)
- /rides/request/
- /rides/<ride_id>/ (detail view)
- /rides/<ride_id>/edit/
- /rides/search/
- /rides/<ride_id>/join/
- /rides/my-rides/

- /admin/

- / (homepage/root URL)
```
### Authentication Flow
![Authentication Flow](./auth_flow.png)
### Driver Registration Flow
![driver registeration Flow](./driver_registration_flow.png)
### request and book rides Flow
![Authentication Flow](./request_book_rides_flow.png)
### share  rides Flow
![Authentication Flow](./share_ride_flow.png)
### Driver Operation Flow
![Authentication Flow](./driver_operation_flow.png)
## Project Overview
