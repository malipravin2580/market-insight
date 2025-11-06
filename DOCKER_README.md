# FastAPI Market Insights - Docker Setup Guide

## Quick Start with Docker Compose (Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Steps

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

3. **Stop services:**
   ```bash
   docker-compose down
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Database: localhost:5432

## Using Docker Only (without Docker Compose)

### Build the image:
```bash
docker build -t market-insights-api .
```

### Run the container:
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:root@host.docker.internal:5432/fast_api_marketinsights \
  --name market-insights-api \
  market-insights-api
```

**Note:** Make sure PostgreSQL is running and accessible before starting the container.

## Database Setup

The database tables will be created automatically when the application starts. If you need to create them manually:

```bash
docker-compose exec api python create_tables.py
```

## Environment Variables

Create a `.env` file to customize:
- `DATABASE_URL`: PostgreSQL connection string (default: postgresql://postgres:root@db:5432/fast_api_marketinsights)
- `PYTHONPATH`: Python path configuration

## Troubleshooting

1. **Check container status:**
   ```bash
   docker-compose ps
   ```

2. **View logs:**
   ```bash
   docker-compose logs api
   docker-compose logs db
   ```

3. **Restart services:**
   ```bash
   docker-compose restart
   ```

4. **Rebuild after code changes:**
   ```bash
   docker-compose up -d --build
   ```

## Volume Mounts

- `./market-insight` - Application code (for development with --reload)
- `./output_data` - Output CSV files and other data

