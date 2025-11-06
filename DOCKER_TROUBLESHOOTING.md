# Docker Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: Permission Denied Error
**Error:** `permission denied while trying to connect to the Docker daemon socket`

**Solution:**
```bash
# Option 1: Add user to docker group (recommended)
sudo usermod -aG docker $USER
# Then logout and login again

# Option 2: Use sudo (temporary)
sudo docker-compose up -d
```

### Issue 2: docker-compose Version Compatibility
**Error:** `Not supported URL scheme http+docker`

**Solutions:**

**Option A: Use Docker Compose v2 (recommended)**
```bash
# If you have Docker 20.10+, use:
docker compose up -d
# (note: no hyphen, it's 'docker compose' not 'docker-compose')
```

**Option B: Update docker-compose**
```bash
# Install latest docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Option C: Use the helper script**
```bash
./docker.sh up
# The script will auto-detect and use the correct version
```

### Issue 3: Docker Daemon Not Running
**Error:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker service
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker
```

## Quick Start (After Fixing Permissions)

1. **Fix permissions:**
   ```bash
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

2. **Start services:**
   ```bash
   # Using helper script
   ./docker.sh up
   
   # OR manually
   docker compose up -d
   # OR
   sudo docker-compose up -d
   ```

3. **Check status:**
   ```bash
   docker ps
   # OR
   sudo docker ps
   ```

4. **View logs:**
   ```bash
   ./docker.sh logs
   # OR
   docker compose logs -f api
   ```

## Manual Docker Commands

If docker-compose continues to have issues, you can run containers manually:

```bash
# Start PostgreSQL
sudo docker run -d \
  --name market_insights_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_DB=fast_api_marketinsights \
  -p 5432:5432 \
  postgres:15-alpine

# Build API image
sudo docker build -t market-insights-api .

# Start API container
sudo docker run -d \
  --name market_insights_api \
  --link market_insights_db:db \
  -e DATABASE_URL=postgresql://postgres:root@db:5432/fast_api_marketinsights \
  -p 8000:8000 \
  market-insights-api
```

