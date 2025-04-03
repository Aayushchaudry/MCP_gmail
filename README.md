# MCP Server for Gmail and Google Calendar Integration

This server implements the Model Context Protocol (MCP) to enable Claude Desktop to interact with Gmail and Google Calendar APIs.

## Features

- **Gmail Integration**
  - Get latest emails from inbox
  - Search for specific emails by query
  - Retrieve email content
  
- **Calendar Integration**
  - Search for calendar events
  - Create new calendar events

## Setup Instructions

### Prerequisites
- Python 3.10 or higher (MCP package requires Python 3.10+)
- A Google Cloud Project with the Gmail and Calendar APIs enabled
- OAuth credentials downloaded as `credentials.json`
- MCP package installed (`pip install mcp[cli]` or `uv add "mcp[cli]"`)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Or using uv (recommended):
   ```
   uv pip install -r requirements.txt
   ```

3. Place your Google OAuth `credentials.json` file in the root directory

### Running the Server

Using the MCP CLI (recommended):
```bash
# Run the server
mcp run server.py

# Run with inspector for debugging
mcp dev server.py
```

Using Python directly:
```bash
# This will attempt to run with uvicorn
python server.py
```

### Connecting to Claude Desktop

The server can be installed in Claude Desktop using the MCP CLI:

```bash
mcp install server.py
```

Alternatively, you can manually configure Claude Desktop with the settings in `claude_desktop_config.json`.

## Implementation Details

This server uses:
- `FastMCP` from the MCP package to create the server
- Google API client libraries for Gmail and Calendar integration
- Pydantic models for request/response validation
- OAuth 2.0 for secure authentication

## Quick Start

For detailed step-by-step instructions, see the [Quick Start Guide](QUICK_START.md).

## Security Notes

- The OAuth token workflow is securely handled
- Tokens are stored locally in `token.pickle`
- Credentials are never exposed to Claude
- All API requests are properly authenticated 