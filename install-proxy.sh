#!/bin/bash

# MCP Proxy Installation Script
# Installs mcp-proxy from https://github.com/sparfenyuk/mcp-proxy

set -e

echo "🚀 Installing MCP Proxy..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install mcp-proxy using uv
echo "📦 Installing mcp-proxy from GitHub..."
uv tool install git+https://github.com/sparfenyuk/mcp-proxy

# Verify installation
if command -v mcp-proxy &> /dev/null; then
    echo "✅ mcp-proxy installed successfully!"
    echo "📋 Version: $(mcp-proxy --version 2>/dev/null || echo 'Version info not available')"
else
    echo "❌ Installation failed. mcp-proxy command not found."
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo "💡 You can now use the run.sh script to start the proxy server."
echo "   Make sure to set your API keys in the environment or .env file first."