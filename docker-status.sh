#!/bin/bash
# Alternative Docker commands that avoid permission errors

echo "🔍 Checking container status..."
sudo docker compose ps

echo ""
echo "📋 View logs (Ctrl+C to exit):"
echo "sudo docker compose logs -f api"

echo ""
echo "✅ Your container is running!"
echo "📍 API: http://localhost:8000"
echo "📍 Docs: http://localhost:8000/docs"
echo ""
echo "💡 Tip: If you need to restart, use:"
echo "   sudo docker restart market_insights_api"

