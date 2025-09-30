# MCP Proxy Guide for Stdio Servers

This guide explains how to use mcp-proxy to expose any stdio-based MCP server via HTTP/SSE endpoints, based on our successful Serper MCP Server implementation.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Docker Integration](#docker-integration)
- [Configuration Options](#configuration-options)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

MCP Proxy allows you to:
- Convert stdio-based MCP servers to HTTP/SSE endpoints
- Enable web-based access to MCP servers
- Scale MCP servers behind load balancers
- Integrate MCP servers with web applications

### Architecture
```
Client → HTTP/SSE → mcp-proxy → stdio → MCP Server
```

## Prerequisites

1. **Install mcp-proxy**:
   ```bash
   # Using uv (recommended)
   uv tool install git+https://github.com/sparfenyuk/mcp-proxy
   
   # Or using pip
   pip install git+https://github.com/sparfenyuk/mcp-proxy
   ```

2. **Verify installation**:
   ```bash
   mcp-proxy --version
   ```

## Basic Usage

### Command Syntax
```bash
mcp-proxy [OPTIONS] <COMMAND> [COMMAND_ARGS...]
```

### Basic Example
```bash
# Expose an MCP server on port 8080
mcp-proxy --host=0.0.0.0 --port=8080 python -m your_mcp_server

# With environment variables
mcp-proxy --host=0.0.0.0 --port=8080 -e API_KEY=your-key python -m your_mcp_server
```

### Common Options
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 8000)
- `--stateless`: Run in stateless mode (recommended for web services)
- `-e KEY=VALUE`: Pass environment variables to the MCP server
- `--cwd`: Set working directory for the MCP server

## Docker Integration

### Method 1: Simple Dockerfile

Create a `Dockerfile` for your MCP server:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv and mcp-proxy
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv tool install git+https://github.com/sparfenyuk/mcp-proxy

# Set working directory
WORKDIR /app

# Copy your MCP server code
COPY . .

# Install your MCP server dependencies
RUN pip install -e .

# Expose port
EXPOSE 8080

# Start with mcp-proxy
CMD ["mcp-proxy", "--host=0.0.0.0", "--port=8080", "--stateless", "python", "-m", "your_mcp_server"]
```

### Method 2: Multi-stage Build (Recommended)

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock* ./
COPY src ./src

# Build dependencies
RUN uv sync --frozen

# Runtime stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv and mcp-proxy
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv tool install git+https://github.com/sparfenyuk/mcp-proxy

# Copy from builder
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src ./src
COPY --from=builder /app/pyproject.toml ./

# Set environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start server
CMD ["mcp-proxy", "--host=0.0.0.0", "--port=8080", "--stateless", "python", "-m", "your_mcp_server"]
```

### Docker Compose

```yaml
services:
  your-mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - HOST=0.0.0.0
      - PORT=8080
      - API_KEY=${API_KEY}
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

## Configuration Options

### Environment Variables
Pass environment variables to your MCP server:

```bash
# Single variable
mcp-proxy -e API_KEY=your-key python -m your_server

# Multiple variables
mcp-proxy \
  -e API_KEY=your-key \
  -e DEBUG=true \
  -e TIMEOUT=30 \
  python -m your_server
```

### Shell Script Wrapper

Create a reusable script:

```bash
#!/bin/bash
# run-mcp-proxy.sh

set -e

# Configuration
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT="8080"
MCP_SERVER_CMD="python -m your_mcp_server"

# Parse arguments
HOST="${1:-$DEFAULT_HOST}"
PORT="${2:-$DEFAULT_PORT}"

echo "🚀 Starting MCP Proxy for Your MCP Server"
echo "🌐 Host: $HOST"
echo "🔌 Port: $PORT"

# Load environment variables
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    set -a
    source .env
    set +a
fi

# Build environment variables for mcp-proxy
ENV_VARS=""
[ ! -z "$API_KEY" ] && ENV_VARS="$ENV_VARS -e API_KEY=$API_KEY"
[ ! -z "$DEBUG" ] && ENV_VARS="$ENV_VARS -e DEBUG=$DEBUG"

echo "🌐 Starting proxy server at http://$HOST:$PORT"
echo "🔗 SSE endpoint: http://$HOST:$PORT/sse"

# Start mcp-proxy
eval "exec mcp-proxy --host=\"$HOST\" --port=\"$PORT\" --stateless $ENV_VARS $MCP_SERVER_CMD"
```

## Examples

### Example 1: SQLite MCP Server

```bash
# Install sqlite MCP server
pip install mcp-server-sqlite

# Run with proxy
mcp-proxy --host=0.0.0.0 --port=8080 -e DATABASE_URL=./data.db python -m mcp_server_sqlite
```

### Example 2: File System MCP Server

```bash
# Run filesystem MCP server
mcp-proxy --host=0.0.0.0 --port=8080 -e ROOT_PATH=/data python -m mcp_server_filesystem
```

### Example 3: Custom MCP Server with Authentication

```bash
# With API key authentication
mcp-proxy \
  --host=0.0.0.0 \
  --port=8080 \
  --stateless \
  -e API_KEY=your-secret-key \
  -e AUTH_REQUIRED=true \
  python -m your_secure_mcp_server
```

## Accessing the Proxy

Once running, your MCP server will be available at:

- **SSE Endpoint**: `http://localhost:8080/sse`
- **Health Check**: `http://localhost:8080/health`

### MCP Client Configuration

Configure your MCP client to use the HTTP endpoint:

```json
{
    "mcpServers": {
        "your-server": {
            "command": "mcp-proxy",
            "args": ["http://localhost:8080/sse"]
        }
    }
}
```

### Testing with curl

```bash
# Health check
curl http://localhost:8080/health

# SSE endpoint (will stream events)
curl -N -H "Accept: text/event-stream" http://localhost:8080/sse
```

## Troubleshooting

### Common Issues

1. **"Connection closed" errors**:
   - Ensure your MCP server starts properly
   - Check environment variables are correctly passed
   - Verify the command syntax

2. **Port already in use**:
   ```bash
   # Find process using port
   lsof -i :8080
   
   # Kill process or use different port
   mcp-proxy --port=8081 python -m your_server
   ```

3. **Environment variables not working**:
   ```bash
   # Debug by printing environment in your MCP server
   import os
   print("Environment:", dict(os.environ))
   ```

4. **setuptools-scm version errors** (for packages using it):
   - Include `.git` directory in Docker builds
   - Or set `SETUPTOOLS_SCM_PRETEND_VERSION` environment variable

### Debug Mode

Enable verbose logging:

```bash
# Add debug logging to your MCP server
mcp-proxy --host=0.0.0.0 --port=8080 -e DEBUG=true python -m your_server
```

### Health Checks

Monitor your proxy:

```bash
# Simple health check script
#!/bin/bash
if curl -f http://localhost:8080/health >/dev/null 2>&1; then
    echo "✅ MCP Proxy is healthy"
else
    echo "❌ MCP Proxy is down"
    exit 1
fi
```

## Best Practices

1. **Use stateless mode** for web services: `--stateless`
2. **Set proper timeouts** for long-running operations
3. **Include health checks** in production deployments
4. **Use environment files** for sensitive data
5. **Implement proper logging** in your MCP server
6. **Use Docker multi-stage builds** for smaller images
7. **Set resource limits** in production containers

## Security Considerations

1. **Environment Variables**: Use `.env` files, not hardcoded values
2. **Network Security**: Bind to specific interfaces in production
3. **Authentication**: Implement API key validation in your MCP server
4. **CORS**: Configure appropriate CORS headers if needed
5. **Rate Limiting**: Consider adding rate limiting for public endpoints

This guide provides a comprehensive foundation for converting any stdio-based MCP server to HTTP/SSE using mcp-proxy, following the same patterns we successfully implemented for the Serper MCP Server.