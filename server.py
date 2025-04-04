#!/usr/bin/env python3
"""
MCP Server for Gmail and Google Calendar integration with Claude Desktop.
"""

import os
import json
import pickle
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("MCP_DEBUG") == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import the MCP package
from mcp.server.fastmcp import FastMCP
# Initialize our MCP server
mcp = FastMCP("gmail_mcp_server")

# Import Google API libraries
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

# Set OAuth environment variables
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Required OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Path to token and credentials files
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.pickle')
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')

# Check authentication status at startup
logger.info(f"Checking authentication status...")
logger.info(f"Token file path: {TOKEN_FILE}")
logger.info(f"Credentials file path: {CREDENTIALS_FILE}")

if not os.path.exists(CREDENTIALS_FILE):
    logger.error(f"Credentials file not found: {CREDENTIALS_FILE}")
else:
    logger.info(f"Credentials file found.")

if not os.path.exists(TOKEN_FILE):
    logger.error(f"Token file not found: {TOKEN_FILE}. Authentication needed.")
else:
    logger.info(f"Token file found. Size: {os.path.getsize(TOKEN_FILE)} bytes")

#------------------------------------------------------------------------------
# Authentication and Service Creation
#------------------------------------------------------------------------------

def get_credentials():
    """Get and refresh OAuth credentials."""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file not found: {CREDENTIALS_FILE}. "
                    "Please download OAuth credentials from Google Cloud Console."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_gmail_service():
    """Get Gmail API service."""
    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_calendar_service():
    """Get Calendar API service."""
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    return service

#------------------------------------------------------------------------------
# Pydantic Models for Request/Response
#------------------------------------------------------------------------------

class EmailMessage(BaseModel):
    """Model for email message data."""
    from_email: str = Field(..., description="Sender's email address")
    subject: str = Field(..., description="Email subject")
    date: str = Field(..., description="Email date")
    id: str = Field(..., description="Email ID")

class EmailContent(BaseModel):
    """Model for email content."""
    id: str = Field(..., description="Email ID")
    subject: str = Field(..., description="Email subject")
    from_email: str = Field(..., description="Sender's email address")
    date: str = Field(..., description="Email date")
    body: str = Field(..., description="Email body content")

class SendEmailRequest(BaseModel):
    """Model for sending email request."""
    to: str = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    cc: Optional[str] = Field(None, description="CC recipients (comma-separated)")
    bcc: Optional[str] = Field(None, description="BCC recipients (comma-separated)")

class SendEmailResponse(BaseModel):
    """Model for send email response."""
    status: str = Field(..., description="Success or error")
    message: str = Field(..., description="Response message")
    email_id: Optional[str] = Field(None, description="ID of the sent email")

class CalendarEvent(BaseModel):
    """Model for calendar event data."""
    id: str = Field(..., description="Event ID")
    summary: str = Field(..., description="Event summary/title")
    start: str = Field(..., description="Start time")
    end: str = Field(..., description="End time")
    location: Optional[str] = Field(None, description="Event location")
    description: Optional[str] = Field(None, description="Event description")

class CalendarEventRequest(BaseModel):
    """Model for calendar event creation request."""
    summary: str = Field(..., description="Event summary/title (60 chars max)")
    start_time: str = Field(..., description="Start time in ISO 8601 UTC format")
    end_time: str = Field(..., description="End time in ISO 8601 UTC format")
    description: Optional[str] = Field(None, description="Event description")
    location: Optional[str] = Field(None, description="Event location")

class CalendarEventResponse(BaseModel):
    """Model for calendar event creation response."""
    status: str = Field(..., description="Success or error")
    event_id: Optional[str] = Field(None, description="Google Calendar event ID")
    htmlLink: Optional[str] = Field(None, description="Event URL")
    message: str = Field(..., description="Human-readable status message")

#------------------------------------------------------------------------------
# Gmail MCP Tools
#------------------------------------------------------------------------------

@mcp.tool()
def get_latest_emails(max_results: int = 10) -> List[EmailMessage]:
    """
    Get the latest emails from Gmail inbox.
    
    Args:
        max_results: Maximum number of emails to retrieve (1-10)
    
    Returns:
        List of email messages with From, Subject, and Date
    """
    if max_results > 10:
        max_results = 10  # Enforce the 10 email limit
    
    try:
        service = get_gmail_service()
        
        # Get list of messages
        results = service.users().messages().list(
            userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return []
        
        # Process each message to extract headers
        email_messages = []
        for message in messages:
            try:
                msg = service.users().messages().get(
                    userId='me', id=message['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']).execute()
                
                headers = msg['payload']['headers']
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                email_messages.append(EmailMessage(
                    from_email=from_email,
                    subject=subject,
                    date=date,
                    id=msg['id']
                ))
            except Exception as e:
                print(f"Error processing message {message['id']}: {e}")
        
        return email_messages
    
    except HttpError as error:
        print(f"Gmail API error: {error}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

@mcp.tool()
def search_emails(query: str, max_results: int = 10) -> List[EmailMessage]:
    """
    Search for emails in Gmail using a query string.
    
    Args:
        query: Gmail search query (e.g., "from:example@gmail.com")
        max_results: Maximum number of emails to retrieve (1-10)
    
    Returns:
        List of email messages matching the search query
    """
    if max_results > 10:
        max_results = 10
    
    try:
        service = get_gmail_service()
        
        # Search for messages
        results = service.users().messages().list(
            userId='me', maxResults=max_results, q=query).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return []
        
        # Process each message to extract headers
        email_messages = []
        for message in messages:
            try:
                msg = service.users().messages().get(
                    userId='me', id=message['id'], format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']).execute()
                
                headers = msg['payload']['headers']
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
                
                email_messages.append(EmailMessage(
                    from_email=from_email,
                    subject=subject,
                    date=date,
                    id=msg['id']
                ))
            except Exception as e:
                print(f"Error processing message {message['id']}: {e}")
        
        return email_messages
    
    except HttpError as error:
        print(f"Gmail API error: {error}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

@mcp.tool()
def get_email_content(email_id: str) -> EmailContent:
    """
    Get the content of a specific email by ID.
    
    Args:
        email_id: The ID of the email to retrieve
    
    Returns:
        Email content including subject, sender, date and body
    """
    try:
        service = get_gmail_service()
        
        # Get the message
        msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
        
        # Extract headers
        headers = msg['payload']['headers']
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        
        # Extract body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body']['data']
                    import base64
                    body = base64.urlsafe_b64decode(body).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            import base64
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        
        return EmailContent(
            id=email_id,
            subject=subject,
            from_email=from_email,
            date=date,
            body=body
        )
    
    except HttpError as error:
        print(f"Gmail API error: {error}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

@mcp.tool()
def send_email(email: SendEmailRequest) -> SendEmailResponse:
    """
    Send an email using Gmail.
    
    Args:
        email: Email details including recipient, subject, and body
    
    Returns:
        Status of email sending operation
    """
    try:
        service = get_gmail_service()
        
        # Create the email message
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import base64
        
        message = MIMEMultipart()
        message['to'] = email.to
        message['subject'] = email.subject
        
        # Add CC and BCC if provided
        if email.cc:
            message['cc'] = email.cc
        if email.bcc:
            message['bcc'] = email.bcc
        
        # Add the body
        msg = MIMEText(email.body)
        message.attach(msg)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send the email
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return SendEmailResponse(
            status="success",
            message="Email sent successfully",
            email_id=sent_message['id']
        )
        
    except HttpError as error:
        logger.error(f"Gmail API error while sending email: {error}")
        return SendEmailResponse(
            status="error",
            message=f"Failed to send email: {str(error)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {e}")
        return SendEmailResponse(
            status="error",
            message=f"Failed to send email: {str(e)}"
        )

#------------------------------------------------------------------------------
# Calendar MCP Tools
#------------------------------------------------------------------------------

@mcp.tool()
def search_events(query: str = "", max_results: int = 10, time_min: Optional[str] = None) -> List[CalendarEvent]:
    """
    Search for events in Google Calendar.
    
    Args:
        query: Search terms to find events
        max_results: Maximum number of events to retrieve
        time_min: Optional minimum time in ISO format (default: now)
    
    Returns:
        List of calendar events matching the search criteria
    """
    try:
        service = get_calendar_service()
        
        # If no time_min provided, use current time
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
            q=query if query else None
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return []
        
        # Process and return the events
        calendar_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            calendar_events.append(CalendarEvent(
                id=event['id'],
                summary=event.get('summary', 'No title'),
                start=start,
                end=end,
                location=event.get('location'),
                description=event.get('description')
            ))
        
        return calendar_events
    
    except HttpError as error:
        print(f"Calendar API error: {error}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

@mcp.tool()
def create_calendar_event(event: CalendarEventRequest) -> CalendarEventResponse:
    """
    Create a new event in Google Calendar.
    
    Args:
        event: Calendar event details
    
    Returns:
        Status of event creation with event ID and link
    """
    try:
        service = get_calendar_service()
        
        # Validate summary length
        if len(event.summary) > 60:
            return CalendarEventResponse(
                status="error",
                message="Event summary exceeds 60 characters limit"
            )
        
        # Create event body
        event_body = {
            'summary': event.summary,
            'start': {
                'dateTime': event.start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event.end_time,
                'timeZone': 'UTC',
            }
        }
        
        # Add optional fields if provided
        if event.description:
            event_body['description'] = event.description
        
        if event.location:
            event_body['location'] = event.location
            
        # Insert the event
        created_event = service.events().insert(
            calendarId='primary', body=event_body).execute()
        
        return CalendarEventResponse(
            status="success",
            event_id=created_event['id'],
            htmlLink=created_event['htmlLink'],
            message=f"Event created successfully: {event.summary}"
        )
    
    except HttpError as error:
        print(f"Calendar API error: {error}")
        return CalendarEventResponse(
            status="error",
            message=f"Calendar API error: {str(error)}"
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        return CalendarEventResponse(
            status="error",
            message=f"Unexpected error: {str(e)}"
        )

if __name__ == "__main__":
    # Show a welcome message
    print("Starting MCP Server for Google API Integration...")
    print("Make sure you have credentials.json in the current directory")
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Warning: Credentials file not found at {CREDENTIALS_FILE}")
        print("Please download OAuth credentials from Google Cloud Console")
    
    # Instructions for running the server
    print("\nThe server is set up and ready.")
    print("To run the server, use one of these commands:")
    print("  mcp run server.py       # Run the server")
    print("  mcp dev server.py       # Run with inspector for debugging")
    print("To install the server in Claude Desktop, use:")
    print("  mcp install server.py") 