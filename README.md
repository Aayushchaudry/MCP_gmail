# MCP Integration Servers

This repository contains MCP (Model Control Protocol) servers for integrating various services with Claude Desktop.

## Gmail and Google Calendar MCP Server

The Gmail and Google Calendar integration allows Claude to interact with your Gmail account and Google Calendar, enabling email management and calendar operations.

### Features

- **Gmail Operations**:
  - Get latest emails from inbox
  - Search emails using Gmail query syntax
  - Read email content
  - Send emails with CC and BCC support

- **Calendar Operations**:
  - Search calendar events
  - Create new calendar events
  - View upcoming events

### Setup Instructions

1. **Prerequisites**:
   - Python 3.x
   - MCP package installed
   - Google Cloud Console project with Gmail and Calendar APIs enabled

2. **OAuth Credentials**:
   - Go to Google Cloud Console
   - Create a new project or select existing one
   - Enable Gmail API and Google Calendar API
   - Create OAuth 2.0 credentials
   - Download credentials and save as `credentials.json` in the project directory

3. **Installation**:
   ```bash
   # Install required packages
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

   # Install the server in Claude Desktop
   mcp install server.py
   ```

4. **First Run**:
   - Run the server: `mcp run server.py`
   - First run will prompt for OAuth authentication
   - Follow the browser link to authorize the application
   - Token will be saved for future use

### Available Tools

#### Gmail Tools
- `get_latest_emails(max_results: int = 10)`: Get latest emails from inbox
- `search_emails(query: str, max_results: int = 10)`: Search emails using Gmail query
- `get_email_content(email_id: str)`: Get content of a specific email
- `send_email(to: str, subject: str, body: str, cc: Optional[str], bcc: Optional[str])`: Send email

#### Calendar Tools
- `search_events(query: str, max_results: int = 10, time_min: Optional[str])`: Search calendar events
- `create_calendar_event(summary: str, start_time: str, end_time: str, description: Optional[str], location: Optional[str])`: Create new event

## Backend API MCP Server

The Backend API MCP server provides a template for integrating your custom backend API with Claude Desktop.

### Features

- User management operations
- Standardized API responses
- Error handling and logging
- Pydantic models for data validation

### Setup Instructions

1. **Prerequisites**:
   - Python 3.x
   - MCP package installed

2. **Installation**:
   ```bash
   # Install required packages
   pip install pydantic

   # Install the server in Claude Desktop
   mcp install backend_server.py
   ```

3. **Configuration**:
   - Update the API endpoint configurations
   - Implement actual API calls in tool functions
   - Add authentication if required

### Available Tools

- `get_users(max_results: int = 10)`: Get list of users
- `create_user(username: str, email: str, password: str)`: Create new user
- `search_users(query: str)`: Search for users

## Development

### Running in Debug Mode

```bash
# Run with debug logging
export MCP_DEBUG=true
mcp dev server.py

# Run without debug logging
mcp run server.py
```

### Adding New Tools

1. Define Pydantic models for request/response
2. Create new tool function with `@mcp.tool()` decorator
3. Implement error handling
4. Add logging for debugging

### Best Practices

- Use appropriate error handling
- Include comprehensive logging
- Validate input data using Pydantic models
- Follow security best practices for API keys and tokens
- Keep credentials and sensitive data secure

## Security Notes

- Store API keys and credentials securely
- Use environment variables for sensitive data
- Never commit credentials to version control
- Implement rate limiting where appropriate
- Follow OAuth best practices



### Common Issues

1. **Authentication Errors**:
   - Check if credentials.json is present
   - Verify OAuth token validity
   - Re-authenticate if token expired

2. **API Rate Limits**:
   - Implement exponential backoff
   - Handle quota exceeded errors
   - Monitor API usage

3. **Connection Issues**:
   - Check network connectivity
   - Verify API endpoint availability
   - Confirm firewall settings

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Create pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 