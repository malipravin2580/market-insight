# Database Connection Summary

## ✅ Configuration Updated

Your project is now configured to connect to your existing PostgreSQL database:

- **Database Name**: `fast_api_marketinsights`
- **Host**: `localhost` (when running locally)
- **Host**: `host.docker.internal` (when running in Docker)
- **Port**: `5432`
- **User**: `postgres`
- **Password**: `root`

## Connection Details

### Local Development (without Docker)
```python
# Uses: postgresql://postgres:root@localhost:5432/fast_api_marketinsights
# Defined in: market-insight/database.py
```

### Docker Container
```yaml
# Uses: postgresql://postgres:root@host.docker.internal:5432/fast_api_marketinsights
# Defined in: docker-compose.yml (DATABASE_URL environment variable)
```

## Verify Connection

### Test from command line:
```bash
psql -h localhost -U postgres -d fast_api_marketinsights
```

### Test from Docker container:
```bash
sudo docker compose exec api python -c "from database import engine; print('✅ Connected!' if engine.connect() else '❌ Failed')"
```

## Tables Expected

Your database should have these tables:
- ✅ `apmc_details` - APMC master data
- ✅ `enaam_records` - eNAM trading records

## Start Application

```bash
# Start Docker container
sudo docker compose up -d

# View logs
sudo docker compose logs -f api

# Access API
# http://localhost:8000
# http://localhost:8000/docs
```

## Troubleshooting

If connection fails:

1. **Check PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   ```

2. **Verify database exists:**
   ```bash
   sudo -u postgres psql -c "\l" | grep fast_api_marketinsights
   ```

3. **Check PostgreSQL allows connections:**
   ```bash
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   ```
   Ensure you have: `host all all 127.0.0.1/32 md5`

4. **Check Docker can reach host:**
   ```bash
   sudo docker compose exec api ping -c 1 host.docker.internal
   ```

