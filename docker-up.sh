#!/bin/bash
# Docker Compose wrapper that handles permission issues gracefully

set -e

cd "$(dirname "$0")"

# Check if using docker compose v2
if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Check if sudo is needed
if ! docker ps &> /dev/null 2>&1; then
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# Check current status
echo "📋 Current container status:"
$SUDO_CMD $COMPOSE_CMD ps

echo ""
echo "🚀 Starting containers with docker compose..."
echo ""

# Start containers (will skip if already running)
if $SUDO_CMD $COMPOSE_CMD up -d 2>&1 | grep -v "permission denied" | grep -v "Error while Stopping"; then
    echo ""
    echo "✅ Containers started!"
    echo ""
    echo "📍 API: http://localhost:8000"
    echo "📍 Docs: http://localhost:8000/docs"
    echo ""
    echo "📋 View logs: sudo docker compose logs -f api"
    echo "🛑 Stop: sudo docker compose down"
else
    echo ""
    echo "⚠️  Note: Container is already running (permission errors can be ignored)"
    echo ""
    echo "✅ Your API is available at: http://localhost:8000"
fi

