#!/bin/bash
# Docker helper script for Market Insights API
# Fixed for compatibility issues

set -e

# Check if running with sudo or as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Note: You may need sudo privileges for Docker commands"
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# Use docker compose (v2) - recommended
if command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    echo "✅ Using Docker Compose v2"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "⚠️  Using Docker Compose v1 (consider upgrading)"
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Check if sudo is needed
if ! docker ps &> /dev/null 2>&1; then
    if sudo docker ps &> /dev/null 2>&1; then
        SUDO_CMD="sudo"
        echo "⚠️  Using sudo for Docker commands"
    else
        echo "❌ Cannot access Docker. Please check Docker service."
        exit 1
    fi
else
    SUDO_CMD=""
fi

case "$1" in
  build)
    echo "Building Docker image..."
    $SUDO_CMD $COMPOSE_CMD build
    ;;
  up)
    echo "Starting services with Docker Compose..."
    $SUDO_CMD $COMPOSE_CMD up -d
    echo ""
    echo "✅ Services started!"
    echo "📍 API available at http://localhost:8000"
    echo "📍 API Docs at http://localhost:8000/docs"
    echo ""
    echo "View logs: ./docker.sh logs"
    echo "Check status: $SUDO_CMD $COMPOSE_CMD ps"
    ;;
  down)
    echo "Stopping services..."
    $SUDO_CMD $COMPOSE_CMD down
    ;;
  logs)
    $SUDO_CMD $COMPOSE_CMD logs -f api
    ;;
  restart)
    echo "Restarting services..."
    $SUDO_CMD $COMPOSE_CMD restart
    ;;
  rebuild)
    echo "Rebuilding and restarting services..."
    $SUDO_CMD $COMPOSE_CMD up -d --build
    ;;
  shell)
    echo "Opening shell in API container..."
    $SUDO_CMD $COMPOSE_CMD exec api /bin/bash
    ;;
  db-shell)
    echo "Opening PostgreSQL shell..."
    $SUDO_CMD $COMPOSE_CMD exec db psql -U postgres -d fast_api_marketinsights
    ;;
  ps)
    echo "Container status:"
    $SUDO_CMD $COMPOSE_CMD ps
    ;;
  fix-permissions)
    echo "Adding current user to docker group..."
    echo "You may need to logout and login again after this."
    sudo usermod -aG docker $USER
    echo ""
    echo "✅ User added to docker group!"
    echo "⚠️  IMPORTANT: Please logout and login again, or run: newgrp docker"
    ;;
  *)
    echo "Usage: $0 {build|up|down|logs|restart|rebuild|shell|db-shell|ps|fix-permissions}"
    echo ""
    echo "Commands:"
    echo "  build            - Build Docker image"
    echo "  up               - Start all services"
    echo "  down             - Stop all services"
    echo "  logs             - View API logs"
    echo "  restart          - Restart services"
    echo "  rebuild          - Rebuild and restart"
    echo "  shell            - Open shell in API container"
    echo "  db-shell         - Open PostgreSQL shell"
    echo "  ps               - Show container status"
    echo "  fix-permissions  - Add user to docker group (requires logout/login)"
    exit 1
    ;;
esac
