#!/bin/bash
# Output debugging information
echo "Starting Gmail MCP Server script at $(date)" >&2
echo "Current directory: $(pwd)" >&2

# Change to the project directory
cd /Users/apple/Desktop/MCP_gmail
echo "Changed to directory: $(pwd)" >&2

# Activate the virtual environment
echo "Activating virtual environment" >&2
source /Users/apple/Desktop/mcp_server/venv_py312/bin/activate
echo "Python version: $(python --version)" >&2
echo "MCP path: $(which mcp)" >&2

# Set debug mode
export MCP_DEBUG=true

# Run the MCP server
echo "Running MCP server" >&2
exec /Users/apple/Desktop/mcp_server/venv_py312/bin/mcp run server.py 