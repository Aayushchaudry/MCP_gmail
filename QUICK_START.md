# Quick Start Guide for Gmail & Google Calendar MCP Server

This guide will help you set up and run the MCP Server for Gmail and Google Calendar integration with Claude Desktop.

## 1. Setup Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API and Google Calendar API
4. Configure the OAuth consent screen:
   - Set the user type as "External"
   - Add scopes for Gmail and Calendar
   - Add your email as a test user
5. Create OAuth 2.0 Client ID credentials:
   - Select "Desktop app" as the application type
   - Download the credentials as `credentials.json`
   - Place this file in the root directory of this project

## 2. Install Dependencies

**Note: The MCP package requires Python 3.10 or higher.**

There are two ways to install the required packages:

### Using pip:
```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using uv (recommended):
```bash
# Install uv if you don't have it
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

## 3. Run the MCP Server

There are two ways to run the MCP server:

### Using the MCP CLI (recommended):
```bash
# Run the server
mcp run server.py

# Run the server with the inspector for debugging
mcp dev server.py
```

### Using Python directly:
```bash
# This will attempt to run with uvicorn
python server.py
```

The first time you run this, a browser window will open asking you to authorize the application to access your Google account. Follow the prompts to complete the authorization.

## 4. Install the MCP Server in Claude Desktop

You can use the `mcp` CLI tool to install the server in Claude Desktop:

```bash
mcp install server.py
```

This will add the server configuration to Claude Desktop. Alternatively, you can manually configure Claude Desktop by importing the `claude_desktop_config.json` file.

## 5. Testing the Integration

Once set up, you can ask Claude to:

- "Show me my latest emails"
- "Search for emails from [specific person]"
- "Show me the content of this email [email ID]"
- "Search my calendar for events about [topic]"
- "Create a calendar event for tomorrow at 2 PM"

## Implemented Functionality

### Gmail
- Get latest emails (`get_latest_emails`)
- Search emails (`search_emails`)
- Get email content (`get_email_content`)

### Google Calendar
- Search events (`search_events`)
- Create calendar event (`create_calendar_event`)

## Troubleshooting

If you encounter issues:

1. Check that your `credentials.json` file is valid and contains the correct OAuth credentials
2. Verify that you've authorized the application with the required scopes
3. If the token is invalid, delete `token.pickle` and restart the server to re-authenticate
4. Make sure the MCP package is properly installed with `pip list | grep mcp`
5. Verify that your Claude Desktop configuration is correct by checking the `claude_desktop_config.json` file

## Security Notes

- Your Google OAuth token is stored locally in `token.pickle`
- No credentials are sent to Claude, only the results of API calls
- The server makes API calls on your behalf based on Claude's requests 