from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class EmailService:
    def __init__(self):
        self.service = self.gmail_authenticate()
        
    def gmail_authenticate(self):
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None

        try:
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_API_CREDENTIALS, 
                    SCOPES
                )
                # Use local redirect URI for testing
                flow.redirect_uri = 'http://localhost:8080'
                creds = flow.run_local_server(
                    port=8080,
                    access_type='offline',
                    include_granted_scopes='true'
                )
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Gmail authentication failed: {str(e)}")
        return None
    def send_ride_confirmation(self, user, ride):
        """Send ride confirmation email to a participant"""
        try:
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
                fail_silently=True  # Changed to True for development
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

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