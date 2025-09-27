# Multi-stage Docker build for Serper MCP Server with Proxy
# Provides HTTP/SSE access to the MCP server via mcp-proxy

FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY src ./src
COPY README.md ./
COPY .git ./.git

# Install the serper-mcp-server package
RUN uv sync --frozen

# Runtime stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install uv in runtime stage
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install mcp-proxy
RUN uv tool install git+https://github.com/sparfenyuk/mcp-proxy

# Set work directory
WORKDIR /app

# Copy the virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy project files
COPY --from=builder /app/src ./src
COPY --from=builder /app/pyproject.toml ./
COPY --from=builder /app/README.md ./
COPY --from=builder /app/.git ./.git

# Copy scripts
COPY run.sh ./
COPY .env.example ./

# Make run script executable
RUN chmod +x run.sh

# Expose the proxy port
EXPOSE 8086

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8086
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8086/health || exit 1

# Default environment variables (can be overridden)
ENV SERPER_API_KEY=""
ENV TAVILY_API_KEY=""
ENV BRAVE_API_KEY=""
ENV JINA_API_KEY=""

# Run the proxy server
CMD ["./run.sh"]