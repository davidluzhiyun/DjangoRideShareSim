import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    def __init__(self):
        self.service = self.gmail_authenticate()
        self.sender = settings.EMAIL_HOST_USER
        
    def gmail_authenticate(self):
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        creds = None
    
        try:
        # Force new token creation
            if os.path.exists('token.json'):
                os.remove('token.json')
                print("Removing old token to force new authentication")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GMAIL_API_CREDENTIALS, 
                SCOPES
            )
        
        # Get new credentials with proper scopes
            creds = flow.run_local_server(
                port=8080,
                access_type='offline',  # Force offline access
                prompt='consent',  # Force consent screen
                include_granted_scopes='true'  # Changed to string 'true' instead of boolean True
            )
        
        # Save new credentials
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                print("New token saved successfully")
            
            service = build('gmail', 'v1', credentials=creds)
        
        # Test connection
            profile = service.users().getProfile(userId='me').execute()
            print(f"Successfully authenticated as: {profile.get('emailAddress')}")
        
            return service
        
        except Exception as e:
            print(f"Gmail authentication failed: {str(e)}")
        return None

    def send_message(self, to_email, subject, msg_html):
        try:
            if not self.service:
                print("Gmail service not initialized")
                return False
            
            message = MIMEMultipart('alternative')
            message['from'] = self.sender
            message['to'] = to_email
            message['subject'] = subject

            msg = MIMEText(msg_html, 'html')
            message.attach(msg)

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw}

            message = (self.service.users().messages().send(
                userId="me", 
                body=body
            ).execute())
            print(f"Message Id: {message['id']}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    def send_ride_confirmation(self, user, ride):
        """Send ride confirmation email to a participant"""
        try:
            subject = 'Ride Confirmation'
            context = {
                'user': user,
                'ride': ride,
                'is_owner': user == ride.owner
            }
            
            html_message = render_to_string('rides/emails/ride_confirmation.html', context)
            return self.send_message(user.email, subject, html_message)
        except Exception as e:
            print(f"Failed to prepare confirmation email: {str(e)}")
            return False
