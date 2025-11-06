# Quick Start Guide

## ✅ Solution: Use Docker Compose v2 with sudo

You have Docker Compose v2 installed! Use these commands:

### Quick Start:
```bash
# Start services (use sudo)
sudo docker compose up -d

# View logs
sudo docker compose logs -f api

# Stop services
sudo docker compose down

# Check status
sudo docker compose ps
```

### Or use the helper script:
```bash
# Start services
./docker.sh up

# View logs
./docker.sh logs

# Stop services
./docker.sh down
```

## 🔧 Fix Docker Permissions (Optional but Recommended)

To avoid using `sudo` every time:

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Apply changes immediately (or logout/login)
newgrp docker

# Now you can use docker without sudo
docker compose up -d
```

## 📝 Important Notes:

1. **Always use `docker compose` (v2)**, NOT `docker-compose` (v1)
2. The `version` field has been removed from docker-compose.yml (obsolete in v2)
3. If you get permission errors, use `sudo` or fix permissions as shown above

## 🚀 What's Running:

- **PostgreSQL Database**: localhost:5433
- **FastAPI Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

