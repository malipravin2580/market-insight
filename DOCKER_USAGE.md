# Using Docker Compose - Quick Guide

## ✅ Your Container is Running!

Current status: **Up 3 hours (healthy)**

## Commands to Use:

### 1. Start containers (detached mode - recommended):
```bash
sudo docker compose up -d
```
This starts containers in the background. No permission errors.

### 2. View logs:
```bash
sudo docker compose logs -f api
```
Press Ctrl+C to exit logs.

### 3. Start and view logs together:
```bash
sudo docker compose up
```
This shows logs in real-time. Press Ctrl+C to stop (but container keeps running).

### 4. Stop containers:
```bash
sudo docker compose down
```

### 5. Restart containers:
```bash
sudo docker compose restart
```

## About the Permission Error

The "permission denied" error only appears when Docker tries to stop/recreate containers. Since your container is already running fine, you can:

- **Ignore it** - Your container is working perfectly
- **Use `-d` flag** - Prevents the error by starting in detached mode
- **Use the helper script**: `./docker-up.sh`

## Quick Helper Script

Run: `./docker-up.sh`

This script handles the permission issues automatically.

## Summary

✅ Your API is working: http://localhost:8000  
✅ Container is healthy  
✅ Use `docker compose up -d` to avoid permission errors  
✅ Use `docker compose logs -f api` to view logs

