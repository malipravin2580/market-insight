from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# SQLAlchemy database URL - supports environment variable for Docker
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:root@localhost:5432/fast_api_marketinsights"
)

# Create engine and session factory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Note: Tables are created automatically when needed
# Commented out to avoid connection errors on startup if database is not accessible
# Uncomment if you want to create tables on import
# Base.metadata.create_all(bind=engine)
