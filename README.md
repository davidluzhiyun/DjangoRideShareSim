# ERSS-HWK1-AR791-ZL303

## Getting Started

### Directory Structure

```
erss-hwk1-ar791-zl303
    ├── README.md
    └── ride_sharing_project
        ├── manage.py
        ├── ride_sharing_project
        │   ├── __init__.py
        │   ├── asgi.py
        │   ├── settings.py
        │   ├── settings.py~
        │   ├── urls.py
        │   └── wsgi.py
        └── rides
            ├── forms
            │   ├── __init__.py
            │   ├── auth_forms.py
            │   ├── driver_forms.py
            │   └── ride_forms.py
            ├── models
            │   ├── __init__.py
            │   ├── driver.py
            │   ├── ride.py
            │   └── ride_sharer.py
            ├── services
            │   ├── __init__.py
            │   ├── email_service.py
            │   ├── ride_service.py
            │   └── search_service.py
            ├── templates
            │   └── rides
            │       ├── auth
            │       ├── base.html
            │       ├── driver
            │       └── ride
            ├── urls
            │   ├── __init__.py
            │   ├── auth_urls.py
            │   ├── driver_urls.py
            │   └── ride_urls.py
            └── views
                ├── __init__.py
                ├── auth_views.py
                ├── driver_views.py
                └── ride_views.py
```
### Authentication Flow
![Authentication Flow](./auth_flow.png)
### Driver Registration Flow
!![driver registeration Flow](./driver_registration_flow.png)
### request and book rides Flow
!![Authentication Flow](./request_book_rides_flow.png)
### share  rides Flow
!![Authentication Flow](./share_ride_flow.png)
### Driver Operation Flow
!![Authentication Flow](./driver_operation_flow.png)
## Project Overview
