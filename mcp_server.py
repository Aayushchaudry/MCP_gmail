#!/usr/bin/env python3
"""
MCP Server for Google API Integration
Enables Claude Desktop to interact with Gmail and Google Calendar.
"""

import os
import logging
import json
from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Optional, Any, Callable, TypeVar, cast

# Import the required Pydantic classes
from pydantic import BaseModel, Field

# Import Google APIs
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Placeholder for the MCP package
# In a real implementation, you would import mcp
# import mcp
class mcp:
    """Placeholder for the MCP package."""
    
    @staticmethod
    def resource():
        """Decorator for MCP resources."""
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def tool():
        """Decorator for MCP tools."""
        def decorator(func):
            return func
        return decorator
    
    @staticmethod
    def serve():
        """Start the MCP server."""
        print("MCP server placeholder - would start serving here")
        print("Note: This is a placeholder implementation. The actual MCP package is required.")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.environ.get("MCP_DEBUG") == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Required OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Token file path
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')

#------------------------------------------------------------------------------
# Authentication and Service Creation
#------------------------------------------------------------------------------

def get_credentials():
    """Get and refresh OAuth credentials."""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(open(TOKEN_FILE).read()), SCOPES)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
    
    # If no valid credentials available, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Credentials refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file not found: {CREDENTIALS_FILE}. "
                    "Please download OAuth credentials from Google Cloud Console."
                )
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("New credentials obtained successfully")
            except Exception as e:
                logger.error(f"Error in authentication flow: {e}")
                raise
        
        # Save the credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            logger.info(f"Credentials saved to {TOKEN_FILE}")
    
    return creds

@lru_cache(maxsize=2)
def get_gmail_service():
    """Get Gmail API service with caching."""
    try:
        creds = get_credentials()
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error creating Gmail service: {e}")
        raise

@lru_cache(maxsize=2)
def get_calendar_service():
    """Get Calendar API service with caching."""
    try:
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Error creating Calendar service: {e}")
        raise

@lru_cache(maxsize=32)
def get_cached_service(api_name: str):
    """Get cached API service based on name."""
    return get_gmail_service() if api_name == 'gmail' else get_calendar_service()

#------------------------------------------------------------------------------
# Pydantic Models for Request/Response
#------------------------------------------------------------------------------

class EmailMessage(BaseModel):
    """Model for email message data."""
    from_email: str = Field(..., description="Sender's email address")
    subject: str = Field(..., description="Email subject")
    date: str = Field(..., description="Email date")
    id: str = Field(..., description="Email ID")

class CalendarEventRequest(BaseModel):
    """Model for calendar event creation request."""
    summary: str = Field(..., description="Event summary/title (60 chars max)")
    start_time: str = Field(..., description="Start time in ISO 8601 UTC format")
    end_time: str = Field(..., description="End time in ISO 8601 UTC format")
    description: Optional[str] = Field(None, description="Event description (markdown)")
    location: Optional[str] = Field(None, description="Event location")

class CalendarEventResponse(BaseModel):
    """Model for calendar event creation response."""
    status: str = Field(..., description="Success or error")
    event_id: Optional[str] = Field(None, description="Google Calendar event ID")
    htmlLink: Optional[str] = Field(None, description="Event URL")
    message: str = Field(..., description="Human-readable status message")

#------------------------------------------------------------------------------
# MCP Resource Endpoints
#------------------------------------------------------------------------------

@mcp.resource()
def auth_status() -> Dict[str, Any]:
    """Check authentication status for Google APIs."""
    try:
        creds_exist = os.path.exists(CREDENTIALS_FILE)
        token_exists = os.path.exists(TOKEN_FILE)
        
        status = {
            "credentials_file_exists": creds_exist,
            "token_file_exists": token_exists,
            "authenticated": False,
            "message": ""
        }
        
        if not creds_exist:
            status["message"] = "Missing credentials.json. Please download from Google Cloud Console."
            return status
        
        if token_exists:
            # Check if token is valid
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(open(TOKEN_FILE).read()), SCOPES)
                status["authenticated"] = creds.valid
                
                if creds.expired and creds.refresh_token:
                    status["message"] = "Token expired but can be refreshed."
                elif creds.valid:
                    status["message"] = "Authenticated and token is valid."
                else:
                    status["message"] = "Token invalid, needs re-authentication."
            except Exception as e:
                status["message"] = f"Error checking token: {str(e)}"
        else:
            status["message"] = "Not authenticated. Run the server and follow prompts."
        
        return status
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return {
            "credentials_file_exists": os.path.exists(CREDENTIALS_FILE),
            "token_file_exists": os.path.exists(TOKEN_FILE),
            "authenticated": False,
            "message": f"Error: {str(e)}"
        }

#------------------------------------------------------------------------------
# Gmail MCP Tools
#------------------------------------------------------------------------------

@mcp.tool()
def get_recent_emails(max_results: int = 10) -> List[EmailMessage]:
    """
    Get recent emails from Gmail.
    
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
            logger.info("No messages found.")
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
                logger.error(f"Error processing message {message['id']}: {e}")
        
        return email_messages
    
    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

#------------------------------------------------------------------------------
# Calendar MCP Tools
#------------------------------------------------------------------------------

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
        logger.error(f"Calendar API error: {error}")
        return CalendarEventResponse(
            status="error",
            message=f"Calendar API error: {str(error)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return CalendarEventResponse(
            status="error",
            message=f"Unexpected error: {str(e)}"
        )

@mcp.tool()
def get_upcoming_events(max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Get upcoming events from Google Calendar.
    
    Args:
        max_results: Maximum number of events to retrieve
    
    Returns:
        List of upcoming calendar events
    """
    try:
        service = get_calendar_service()
        
        # Get current time in ISO format
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            logger.info('No upcoming events found.')
            return []
        
        # Process and return the events
        upcoming_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            upcoming_events.append({
                'summary': event.get('summary', 'No title'),
                'start': start,
                'end': event['end'].get('dateTime', event['end'].get('date')),
                'htmlLink': event.get('htmlLink', ''),
                'id': event['id']
            })
        
        return upcoming_events
    
    except HttpError as error:
        logger.error(f"Calendar API error: {error}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

#------------------------------------------------------------------------------
# Main Function
#------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        # Show a welcome message
        print("Starting MCP Server for Google API Integration...")
        print(f"Debug mode: {'ON' if os.environ.get('MCP_DEBUG') == 'true' else 'OFF'}")
        
        # Check if credentials file exists
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Warning: Credentials file not found at {CREDENTIALS_FILE}")
            print("Please download OAuth credentials from Google Cloud Console")
        
        # Start the MCP server
        mcp.serve()
    except Exception as e:
        logger.critical(f"Failed to start MCP server: {e}")
        raise 