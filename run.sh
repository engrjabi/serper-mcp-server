#!/bin/bash

# MCP Proxy Runner Script
# Runs serper-mcp-server via mcp-proxy with SSE endpoint

set -e

# Default configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8086"
DEFAULT_PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse command line arguments
HOST="${1:-$DEFAULT_HOST}"
PORT="${2:-$DEFAULT_PORT}"
PROJECT_DIR="${3:-$DEFAULT_PROJECT_DIR}"

echo "🚀 Starting MCP Proxy for Serper MCP Server"
echo "📁 Project directory: $PROJECT_DIR"
echo "🌐 Host: $HOST"
echo "🔌 Port: $PORT"

# Change to project directory
cd "$PROJECT_DIR"

# Check if mcp-proxy is installed
if ! command -v mcp-proxy &> /dev/null; then
    echo "❌ Error: mcp-proxy is not installed."
    echo "   Please run ./install-proxy.sh first"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

# Check for required API key
if [ -z "$SERPER_API_KEY" ]; then
    echo "⚠️  Warning: SERPER_API_KEY is not set."
    echo "   Please set it as an environment variable or in a .env file."
    echo ""
    echo "   Example .env file:"
    echo "   SERPER_API_KEY=your-serper-api-key-here"
    echo "   TAVILY_API_KEY=your-tavily-api-key-here"
    echo "   BRAVE_API_KEY=your-brave-api-key-here"
    echo "   JINA_API_KEY=your-jina-api-key-here"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Display configured API keys (masked)
echo "🔑 API Keys configured:"
[ ! -z "$SERPER_API_KEY" ] && echo "   ✅ SERPER_API_KEY: ${SERPER_API_KEY:0:6}***"
[ ! -z "$TAVILY_API_KEY" ] && echo "   ✅ TAVILY_API_KEY: ${TAVILY_API_KEY:0:6}***"
[ ! -z "$BRAVE_API_KEY" ] && echo "   ✅ BRAVE_API_KEY: ${BRAVE_API_KEY:0:6}***"
[ ! -z "$JINA_API_KEY" ] && echo "   ✅ JINA_API_KEY: ${JINA_API_KEY:0:6}***"

# Build environment variables for uv run serper-mcp-server
ENV_VARS=""
[ ! -z "$SERPER_API_KEY" ] && ENV_VARS="$ENV_VARS --env SERPER_API_KEY \"$SERPER_API_KEY\""
[ ! -z "$TAVILY_API_KEY" ] && ENV_VARS="$ENV_VARS --env TAVILY_API_KEY \"$TAVILY_API_KEY\""
[ ! -z "$BRAVE_API_KEY" ] && ENV_VARS="$ENV_VARS --env BRAVE_API_KEY \"$BRAVE_API_KEY\""
[ ! -z "$JINA_API_KEY" ] && ENV_VARS="$ENV_VARS --env JINA_API_KEY \"$JINA_API_KEY\""

echo ""
echo "🌐 Starting proxy server at http://$HOST:$PORT"
echo "🔗 SSE endpoint: http://$HOST:$PORT/sse"
echo "📡 Use this URL in your MCP client configuration"
echo ""
echo "Press Ctrl+C to stop the server"
echo "─────────────────────────────────────────────────"

# Start mcp-proxy with the serper-mcp-server
eval "exec mcp-proxy --host=\"$HOST\" --port=\"$PORT\" --stateless uv run serper-mcp-server $ENV_VARS"