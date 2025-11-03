#!/usr/bin/env python3
"""
Create database tables for FastAPI Market Insights application.
This script creates the PostgreSQL database and all required tables.
"""

import sys
import os

# Add the market-insight directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'market-insight'))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL, engine
from models import Base

def create_database():
    """Create the database if it doesn't exist"""
    # Extract database name from URL
    db_url_without_db = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[0]
    db_name = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[1]
    
    # Connect to postgres database to create the target database
    admin_engine = create_engine(db_url_without_db + '/postgres')
    
    try:
        with admin_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
            ))
            exists = result.fetchone()
            
            if not exists:
                # Terminate any existing connections
                conn.execute(text(f"""
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
                """))
                
                # Create database
                conn.commit()
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                conn.commit()
                print(f"✅ Database '{db_name}' created successfully!")
            else:
                print(f"ℹ️  Database '{db_name}' already exists.")
    except Exception as e:
        print(f"⚠️  Could not create database (might already exist): {e}")
    finally:
        admin_engine.dispose()

def create_tables():
    """Create all tables defined in models"""
    try:
        print("\nCreating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("FastAPI Market Insights - Database Setup")
    print("=" * 60)
    
    create_database()
    create_tables()
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed!")
    print("=" * 60)

