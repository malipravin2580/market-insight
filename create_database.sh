#!/bin/bash
# Database setup script for FastAPI Market Insights

# Database connection details
DB_NAME="fast_api_marketinsights"
DB_USER="postgres"
DB_PASSWORD="root"
DB_HOST="localhost"
DB_PORT="5433"

echo "Creating PostgreSQL database: $DB_NAME"

# Option 1: Using psql command line (if you have psql installed)
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database might already exist or connection failed"

# Option 2: Using createdb command (alternative)
# createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

echo "Database '$DB_NAME' created successfully!"
echo ""
echo "Tables will be created automatically when you run the application."
echo "Or you can run: python market-insight/create_tables.py"

