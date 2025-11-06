# Connect Docker Container to Existing PostgreSQL Database

## Configuration Updated ✅

Your Docker setup is now configured to connect to your existing PostgreSQL database `marketinsights` running on the host machine.

## Important: PostgreSQL Configuration

For Docker containers to connect to your host PostgreSQL, you need to ensure PostgreSQL allows connections:

### 1. Check PostgreSQL Configuration

Edit PostgreSQL config file (usually `/etc/postgresql/*/main/postgresql.conf`):
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Ensure this line exists:
```
listen_addresses = '*'
```

### 2. Update PostgreSQL Authentication

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Add this line (for Docker containers):
```
host    all             all             172.17.0.0/16           md5
```

### 3. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```

### 4. Verify Database Exists
```bash
sudo -u postgres psql -c "\l" | grep marketinsights
```

If database doesn't exist, create it:
```bash
sudo -u postgres psql -c "CREATE DATABASE marketinsights;"
```

## Start Docker Container

```bash
# Start the API container
sudo docker compose up -d

# View logs
sudo docker compose logs -f api
```

## Connection Details

- **Host Database**: `localhost:5432/marketinsights`
- **From Docker Container**: `host.docker.internal:5432/marketinsights`
- **API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

## Troubleshooting

If you get connection errors:

1. **Check PostgreSQL is running:**
   ```bash
   sudo systemctl status postgresql
   ```

2. **Test connection from host:**
   ```bash
   psql -h localhost -U postgres -d marketinsights
   ```

3. **Check PostgreSQL logs:**
   ```bash
   sudo tail -f /var/log/postgresql/postgresql-*-main.log
   ```

4. **Check Docker container logs:**
   ```bash
   sudo docker compose logs api
   ```

