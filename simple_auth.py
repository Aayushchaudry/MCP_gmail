#!/usr/bin/env python3
"""
Simplified Google OAuth authentication.
"""

import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set OAuth environment variables
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Required scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def main():
    print("Simple Google OAuth Authentication")
    print("=================================\n")
    
    # Load the credentials file
    try:
        with open('credentials.json', 'r') as f:
            cred_data = json.load(f)
        
        # Print some info about the project
        if 'installed' in cred_data:
            project_id = cred_data['installed'].get('project_id', 'Unknown')
            client_id = cred_data['installed'].get('client_id', 'Unknown')
            print(f"Project ID: {project_id}")
            print(f"Client ID: {client_id[:15]}...{client_id[-10:]}\n")
    except Exception as e:
        print(f"Error reading credentials.json: {e}")
        return
    
    print("Starting authentication process...")
    print("\nIMPORTANT INSTRUCTIONS:")
    print("1. A browser window will open")
    print("2. When you see 'Google hasn't verified this app' screen:")
    print("   - Click 'Advanced' link at bottom left")
    print("   - Click 'Go to [Your Project Name] (unsafe)' at bottom")
    print("3. Sign in with your Google account")
    print("4. When asked for permissions, click 'Continue'\n")
    
    input("Press Enter to continue...")
    
    try:
        # Create the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',
            SCOPES,
            redirect_uri='http://localhost:8090'
        )
        
        # Run the OAuth flow
        creds = flow.run_local_server(
            port=8090,
            prompt='consent',
            authorization_prompt_message='Please visit this URL to authorize this application: {url}',
            success_message='Authentication successful! You can close this window now.'
        )
        
        # Save the credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("\nAuthentication successful!")
        print(f"Token saved to: {os.path.abspath('token.pickle')}")
        
        # Test Gmail API access
        print("\nTesting Gmail API access...")
        try:
            gmail = build('gmail', 'v1', credentials=creds)
            profile = gmail.users().getProfile(userId='me').execute()
            print(f"Successfully connected to Gmail for: {profile.get('emailAddress')}")
        except Exception as e:
            print(f"Gmail API test failed: {e}")
        
        print("\nYou can now start the MCP server and use it with Claude Desktop.")
        
    except Exception as e:
        print(f"\nError during authentication: {e}")

if __name__ == "__main__":
    main() 