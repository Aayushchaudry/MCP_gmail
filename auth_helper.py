#!/usr/bin/env python3
"""
Helper script to authenticate with Google and create a token.pickle file.
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import sys

# Required OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

# Path to token and credentials files
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def authenticate():
    """Authenticate with Google and save the token."""
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Refreshed existing token.")
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials file not found: {CREDENTIALS_FILE}. "
                    "Please download OAuth credentials from Google Cloud Console."
                )
            
            print(f"Starting authentication flow using {CREDENTIALS_FILE}...")
            print("\nIMPORTANT: When you see the 'Google hasn't verified this app' screen:")
            print("1. Click on 'Advanced'")
            print("2. Click on 'Go to [Project Name] (unsafe)'")
            print("3. Sign in with your Google account")
            print("4. Click 'Continue' to grant the requested permissions\n")
            
            # Enable OAuthlib to work with unverified apps in a development environment
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
            os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, 
                SCOPES,
                # Set redirect_uri to make authentication easier
                redirect_uri='http://localhost:8080'
            )
            
            # For local debugging, use the local server
            creds = flow.run_local_server(port=8080)
            print("Authentication successful!")
        
        # Save the credentials for future use
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
            print(f"Token saved to {TOKEN_FILE}")
    else:
        print("Existing token is valid.")
    
    return creds

if __name__ == "__main__":
    print("Google Authentication Helper")
    print("---------------------------")
    try:
        creds = authenticate()
        print("\nAuthentication process completed successfully!")
        print(f"Token file created at: {os.path.abspath(TOKEN_FILE)}")
        print("\nYou can now use the MCP server with Claude Desktop.")
    except Exception as e:
        print(f"Error during authentication: {e}") 