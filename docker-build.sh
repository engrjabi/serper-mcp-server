#!/bin/bash

# Docker build and test script for Serper MCP Server

set -e

echo "🐳 Building Serper MCP Server Docker Image"
echo "=========================================="

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t serper-mcp-server:latest .

echo ""
echo "✅ Build completed successfully!"

# Check if .env file exists for testing
if [ -f ".env" ]; then
    echo ""
    echo "🧪 Testing the Docker container..."
    
    # Run a test container
    echo "🚀 Starting test container..."
    CONTAINER_ID=$(docker run -d \
        --name serper-mcp-test \
        -p 8087:8086 \
        --env-file .env \
        serper-mcp-server:latest)
    
    echo "📦 Container ID: $CONTAINER_ID"
    
    # Wait for container to start
    echo "⏳ Waiting for container to start (30 seconds)..."
    sleep 30
    
    # Test health endpoint
    echo "🔍 Testing health endpoint..."
    if curl -f http://localhost:8087/health 2>/dev/null; then
        echo "✅ Health check passed!"
    else
        echo "❌ Health check failed"
        echo "📋 Container logs:"
        docker logs serper-mcp-test
    fi
    
    # Clean up test container
    echo "🧹 Cleaning up test container..."
    docker stop serper-mcp-test >/dev/null 2>&1 || true
    docker rm serper-mcp-test >/dev/null 2>&1 || true
    
    echo ""
    echo "🎉 Docker build and test completed!"
    echo ""
    echo "To run the container:"
    echo "  docker run -d --name serper-mcp-server -p 8086:8086 --env-file .env serper-mcp-server:latest"
    echo ""
    echo "To use Docker Compose:"
    echo "  docker-compose up -d"
else
    echo ""
    echo "⚠️  No .env file found. Skipping container test."
    echo "   Create a .env file with your API keys to test the container."
    echo ""
    echo "🎉 Docker build completed!"
    echo ""
    echo "To run the container with environment variables:"
    echo "  docker run -d --name serper-mcp-server -p 8086:8086 -e SERPER_API_KEY=your-key serper-mcp-server:latest"
fi