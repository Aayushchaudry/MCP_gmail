# Using Gmail and Calendar Integration with Claude Desktop

This guide shows you how to interact with Gmail and Google Calendar through Claude Desktop using the MCP server.

## Prerequisites

1. **Server is running**: Make sure the MCP server is running with `mcp run server.py`
2. **Server is installed in Claude**: Verify the server was installed with `mcp install server.py`
3. **Claude Desktop is open**: Launch Claude Desktop and ensure it's connected to the MCP server

## Gmail Commands

Here are some examples of how to ask Claude to interact with your Gmail:

### Viewing Recent Emails

```
Show me my latest emails.
```

### Searching for Specific Emails

```
Search my emails for messages from john@example.com
```

```
Find emails with "meeting" in the subject line
```

### Reading Email Content

First, get the email ID from one of the search results, then:

```
Show me the content of email [email_id]
```

## Calendar Commands

Here are some examples of how to interact with your Google Calendar:

### Searching for Events

```
Search my calendar for meetings next week
```

```
Find events containing "project review"
```

### Creating Calendar Events

```
Create a calendar event titled "Team Meeting" tomorrow from 2pm to 3pm
```

```
Schedule a meeting with John on Friday at 10am for 45 minutes about "Project Update"
```

## Troubleshooting

If Claude says it can't connect to Gmail or Calendar:

1. Make sure the MCP server is running in a terminal window
2. Check that you've completed the OAuth authentication flow
3. Verify that Claude Desktop is properly configured with the MCP server
4. Try restarting Claude Desktop

## Security & Privacy

- The MCP server runs locally on your machine
- Your email contents and calendar details never leave your computer
- Claude only has access to the data returned by the specific API calls you authorize 