#!/bin/bash
# Quick fix script for docker-compose issues

echo "🔧 Docker Compose Troubleshooting Script"
echo "=========================================="
echo ""

# Check Docker daemon
echo "1. Checking Docker daemon..."
if docker ps &> /dev/null; then
    echo "   ✅ Docker daemon is accessible"
elif sudo docker ps &> /dev/null; then
    echo "   ⚠️  Docker requires sudo"
    USE_SUDO="sudo"
else
    echo "   ❌ Docker daemon not accessible"
    echo "   Starting Docker service..."
    sudo systemctl start docker
    USE_SUDO="sudo"
fi

# Try Docker Compose v2 first
echo ""
echo "2. Trying Docker Compose v2..."
if docker compose version &> /dev/null 2>&1; then
    echo "   ✅ Docker Compose v2 found!"
    echo ""
    echo "🚀 Starting services with Docker Compose v2..."
    $USE_SUDO docker compose up -d
    echo ""
    echo "✅ Services started! Check status with: docker compose ps"
    exit 0
fi

# If v2 doesn't work, try updating docker-compose v1
echo "   ⚠️  Docker Compose v2 not available"
echo ""
echo "3. Installing/Updating Docker Compose v2..."
echo "   Downloading latest docker-compose..."

# Download latest docker-compose v2
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose-v2
sudo chmod +x /usr/local/bin/docker-compose-v2

if [ -f /usr/local/bin/docker-compose-v2 ]; then
    echo "   ✅ Docker Compose v2 installed"
    echo ""
    echo "🚀 Starting services with Docker Compose v2..."
    $USE_SUDO /usr/local/bin/docker-compose-v2 up -d
    echo ""
    echo "✅ Services started!"
    echo "💡 Tip: You can create an alias: alias docker-compose='/usr/local/bin/docker-compose-v2'"
else
    echo "   ❌ Failed to install Docker Compose v2"
    echo ""
    echo "🔄 Falling back to manual Docker commands..."
    echo ""
    
    # Manual Docker commands
    echo "Starting PostgreSQL container..."
    $USE_SUDO docker run -d \
      --name market_insights_db \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=root \
      -e POSTGRES_DB=fast_api_marketinsights \
      -p 5433:5433 \
      postgres:15-alpine
    
    echo "Building API image..."
    $USE_SUDO docker build -t market-insights-api .
    
    echo "Starting API container..."
    $USE_SUDO docker run -d \
      --name market_insights_api \
      --link market_insights_db:db \
      -e DATABASE_URL=postgresql://postgres:root@db:5433/fast_api_marketinsights \
      -p 8000:8000 \
      market-insights-api
    
    echo ""
    echo "✅ Containers started manually!"
    echo "Check status with: docker ps"
fi

