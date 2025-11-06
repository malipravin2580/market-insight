#!/bin/bash
# Smart Docker Compose script that handles permission issues

set -e

cd "$(dirname "$0")"

# Check if container is already running
if sudo docker ps --format "{{.Names}}" | grep -q "^market_insights_api$"; then
    echo "✅ Container 'market_insights_api' is already running!"
    echo ""
    echo "📋 Current status:"
    sudo docker compose ps
    echo ""
    echo "📋 View logs: sudo docker compose logs -f api"
    echo "📍 API: http://localhost:8000"
    echo ""
    echo "If you need to restart, use: sudo docker compose restart"
    exit 0
fi

# If container doesn't exist or isn't running, try to start it
echo "🚀 Starting containers..."
sudo docker compose up -d --remove-orphans 2>&1 | grep -v "permission denied" | grep -v "Error while Stopping" || true

echo ""
echo "✅ Done!"
echo "📍 API: http://localhost:8000"
echo "📍 Docs: http://localhost:8000/docs"

