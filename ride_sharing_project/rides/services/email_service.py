# rides/services/email_service.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

class EmailService:
    """
    Service class to handle all email notifications
    """
    
    def send_ride_confirmation(self, user, ride):
        """Send ride confirmation email to a participant"""
        subject = 'Ride Confirmation'
        context = {
            'user': user,
            'ride': ride,
            'ride_url': reverse('rides:detail', args=[ride.id]),
            'is_owner': user == ride.owner,
            'is_sharer': ride.sharers.filter(user=user).exists()
        }
        
        html_message = render_to_string('rides/emails/ride_confirmation.html', context)
        plain_message = render_to_string('rides/emails/ride_confirmation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )

    def send_ride_completion_notification(self, ride):
        """Send ride completion notification to all participants"""
        subject = 'Ride Completed'
        participants = [ride.owner] + [sharer.user for sharer in ride.sharers.all()]
        
        for user in participants:
            context = {
                'user': user,
                'ride': ride,
                'is_owner': user == ride.owner
            }
            
            html_message = render_to_string('rides/emails/ride_completion.html', context)
            plain_message = render_to_string('rides/emails/ride_completion.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

    def send_ride_cancellation(self, ride):
        """Send ride cancellation notification to all participants"""
        subject = 'Ride Cancelled'
        participants = [ride.owner] + [sharer.user for sharer in ride.sharers.all()]
        
        if ride.driver:
            participants.append(ride.driver.driver)
        
        for user in participants:
            context = {
                'user': user,
                'ride': ride,
                'is_owner': user == ride.owner,
                'is_driver': ride.driver and user == ride.driver.driver
            }
            
            html_message = render_to_string('rides/emails/ride_cancellation.html', context)
            plain_message = render_to_string('rides/emails/ride_cancellation.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )