import os
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class EmailManager:
    def __init__(self, config):
        self.config = config
        self.credentials_file = config.GMAIL_CREDENTIALS_FILE
        self.token_file = config.GMAIL_TOKEN_FILE
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
                  'https://www.googleapis.com/auth/gmail.send',
                  'https://www.googleapis.com/auth/gmail.modify']
        
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"Credentials file not found: {self.credentials_file}")
                    logger.info("Please download credentials.json from Google Cloud Console")
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail authentication successful")
        except Exception as e:
            logger.error(f"Gmail authentication failed: {e}")
    
    def send_email(self, to: str, subject: str, body: str, 
                   cc: Optional[str] = None, bcc: Optional[str] = None,
                   attachments: List[str] = None) -> bool:
        """Send an email"""
        try:
            if not self.service:
                logger.error("Gmail service not available")
                return False
            
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            
            # Add body
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            sent_message = self.service.users().messages().send(
                userId='me', body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email sent successfully: {sent_message['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def get_emails(self, max_results: int = 10, query: str = None) -> List[Dict[str, Any]]:
        """Get emails from inbox"""
        try:
            if not self.service:
                logger.error("Gmail service not available")
                return []
            
            # Build query
            if not query:
                query = "in:inbox"
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'snippet': snippet,
                    'thread_id': msg.get('threadId', '')
                })
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting emails: {e}")
            return []
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails"""
        return self.get_emails(max_results, "is:unread")
    
    def get_recent_emails(self, days: int = 7, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent emails"""
        date_query = f"after:{days}d"
        return self.get_emails(max_results, date_query)
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read"""
        try:
            if not self.service:
                return False
            
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            logger.info(f"Marked message {message_id} as read")
            return True
            
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            return False
    
    def delete_email(self, message_id: str) -> bool:
        """Delete an email"""
        try:
            if not self.service:
                return False
            
            self.service.users().messages().delete(
                userId='me', id=message_id
            ).execute()
            
            logger.info(f"Deleted message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails"""
        return self.get_emails(max_results, query)
    
    def get_email_content(self, message_id: str) -> str:
        """Get full email content"""
        try:
            if not self.service:
                return "Gmail service not available"
            
            message = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            # Extract text content
            if 'payload' in message:
                payload = message['payload']
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                
                # If no parts, try body
                if 'body' in payload and 'data' in payload['body']:
                    data = payload['body']['data']
                    return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return "Could not extract email content"
            
        except Exception as e:
            logger.error(f"Error getting email content: {e}")
            return f"Error: {str(e)}"
    
    def format_emails_summary(self, emails: List[Dict[str, Any]]) -> str:
        """Format emails as a readable summary"""
        if not emails:
            return "No emails found."
        
        summary = []
        for i, email in enumerate(emails, 1):
            summary.append(
                f"{i}. From: {email['sender']}\n"
                f"   Subject: {email['subject']}\n"
                f"   Date: {email['date']}\n"
                f"   Snippet: {email['snippet'][:100]}...\n"
            )
        
        return "\n".join(summary)
    
    def is_authenticated(self) -> bool:
        """Check if Gmail is authenticated"""
        return self.service is not None



