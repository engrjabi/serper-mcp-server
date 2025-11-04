# Serper MCP Server
[![smithery badge](https://smithery.ai/badge/@garylab/serper-mcp-server)](https://smithery.ai/server/@garylab/serper-mcp-server)

A Model Context Protocol server that provides **Google Search via Serper**. This server enables LLMs to get search result information from Google.

## Available Tools

- `google_search` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_images` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_videos` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_places` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_maps` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_reviews` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_news` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_shopping` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_lens` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_scholar` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_parents` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `google_search_autocomplete` - Set [all the parameters](src/serper_mcp_server/schemas.py)
- `webpage_scrape` - Set [all the parameters](src/serper_mcp_server/schemas.py)

## Multi-Service Fallback Support

This server now includes **automatic fallback support** across multiple search and scrape services for enhanced reliability:

### Search Services (in priority order):
1. **Serper** (primary) - Google Search via Serper API
2. **Tavily** (fallback) - AI-optimized search results
3. **Brave** (fallback) - Independent web search
4. **Jina** (fallback) - AI-powered search via s.jina.ai

### Scrape Services (in priority order):
1. **Serper** (primary) - Web scraping via Serper API  
2. **Jina** (fallback) - Clean Markdown content extraction

The server automatically tries each service in order when the previous one fails (non-2XX HTTP responses). This ensures maximum uptime and reliability.

### Additional API Keys (Optional)

To enable fallback services, add these optional environment variables:

```bash
TAVILY_API_KEY=your-tavily-api-key-here
BRAVE_API_KEY=your-brave-api-key-here  
JINA_API_KEY=your-jina-api-key-here
```

**Note**: Only `SERPER_API_KEY` is required. Other keys are optional for fallback functionality.

## Usage

### Installing via Smithery

To install Serper MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@garylab/serper-mcp-server):

```bash
npx -y @smithery/cli install @garylab/serper-mcp-server --client claude
```

### Using `uv` (recommended)

1. Make sure you had installed [`uv`](https://docs.astral.sh/uv/) on your os system.

2. In your MCP client code configuration or **Claude** settings (file `claude_desktop_config.json`) add `serper` mcp server:
    ```json
    {
        "mcpServers": {
            "serper": {
                "command": "uvx",
                "args": ["serper-mcp-server"],
                "env": {
                    "SERPER_API_KEY": "<Your Serper API key>"
                }
            }
        }
    }
    ```
    `uv` will download mcp server automatically using `uvx` from [pypi.org](https://pypi.org/project/serper-mcp-server/) and apply to your MCP client.

### Using `pip` for project
1. Add `serper-mcp-server` to your MCP client code `requirements.txt` file.
    ```txt
    serper-mcp-server
    ```

2. Install the dependencies.
    ```shell
    pip install -r requirements.txt
    ```

3. Add the configuration for you client:
    ```json
    {
        "mcpServers": {
            "serper": {
                "command": "python3",
                "args": ["-m", "serper_mcp_server"],
                "env": {
                    "SERPER_API_KEY": "<Your Serper API key>"
                }
            }
        }
    }
    ```


### Using `pip` for globally usage

1. Make sure the `pip` or `pip3` is in your os system.
    ```bash
    pip install serper-mcp-server
    # or
    pip3 install serper-mcp-server
    ```

2. MCP client code configuration or **Claude** settings, add `serper` mcp server:
    ```json
    {
        "mcpServers": {
            "serper": {
                "command": "python3",
                "args": ["serper-mcp-server"],
                "env": {
                    "SERPER_API_KEY": "<Your Serper API key>"
                }
            }
        }
    }
    ```


## Using MCP Proxy (HTTP/SSE Access)

For HTTP/SSE access to the MCP server, you can use mcp-proxy to expose the server over HTTP.

### Installation

1. First, install mcp-proxy:
   ```bash
   ./install-proxy.sh
   ```

2. Set your API keys in a `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. Run the proxy server:
   ```bash
   ./run.sh
   ```

   Or with custom host/port:
   ```bash
   ./run.sh 0.0.0.0 8086
   ```

### Accessing the Server

Once running, the server will be available at:
- **SSE Endpoint**: `http://localhost:8086/sse`
- **Health Check**: `http://localhost:8086/health`

### MCP Client Configuration for HTTP

Configure your MCP client to use the HTTP endpoint:

```json
{
    "mcpServers": {
        "serper": {
            "command": "mcp-proxy",
            "args": ["http://localhost:8086/sse"],
            "env": {
                "API_ACCESS_TOKEN": "your-token-if-needed"
            }
        }
    }
}
```

## Debugging

You can use the MCP inspector to debug the server. For `uvx` installations:

```bash
npx @modelcontextprotocol/inspector uvx serper-mcp-server
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
git clone https://github.com/garylab/serper-mcp-server.git
cd serper-mcp-server
npx @modelcontextprotocol/inspector uv run serper-mcp-server -e SERPER_API_KEY=<the key>
```

For HTTP proxy debugging:
```bash
# Test the HTTP endpoint
curl http://localhost:8086/health

# Use inspector with proxy
npx @modelcontextprotocol/inspector http://localhost:8086/sse
```

## Docker Deployment

For containerized deployment, you can use Docker to run the MCP server with proxy in an isolated environment.

### Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone https://github.com/garylab/serper-mcp-server.git
   cd serper-mcp-server
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

The server will be available at `http://localhost:8086` with the SSE endpoint at `http://localhost:8086/sse`.

### Docker Commands

**Build the image**:
```bash
docker build -t serper-mcp-server .
```

**Run the container**:
```bash
docker run -d \
  --name serper-mcp-server \
  -p 8086:8086 \
  -e SERPER_API_KEY="your-serper-api-key" \
  -e TAVILY_API_KEY="your-tavily-api-key" \
  -e BRAVE_API_KEY="your-brave-api-key" \
  -e JINA_API_KEY="your-jina-api-key" \
  serper-mcp-server
```

**Using environment file**:
```bash
docker run -d \
  --name serper-mcp-server \
  -p 8086:8086 \
  --env-file .env \
  serper-mcp-server
```

### Docker Compose Options

**Production deployment**:
```bash
docker-compose up -d
```

**Development with live code changes**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**View logs**:
```bash
docker-compose logs -f serper-mcp-server
```

**Stop the service**:
```bash
docker-compose down
```

### Environment Variables

The Docker container accepts the following environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `SERPER_API_KEY` | Yes | Your Serper API key |
| `TAVILY_API_KEY` | No | Tavily API key for fallback search |
| `BRAVE_API_KEY` | No | Brave Search API key for fallback |
| `JINA_API_KEY` | No | Jina API key for fallback scraping |
| `HOST` | No | Server host (default: 0.0.0.0) |
| `PORT` | No | Server port (default: 8086) |

### Health Check

The Docker container includes a health check endpoint:
```bash
curl http://localhost:8086/health
```

### Docker Hub

*(Future)* The image will be available on Docker Hub:
```bash
docker pull garylab/serper-mcp-server:latest
```

## License

serper-mcp-server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
