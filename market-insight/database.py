from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "fast_api_marketinsights")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")

# Construct DATABASE_URL if not provided directly
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# SQLAlchemy database URL - supports environment variable for Docker
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Create engine and session factory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Note: Tables are created automatically when needed
# Commented out to avoid connection errors on startup if database is not accessible
# Uncomment if you want to create tables on import
# Base.metadata.create_all(bind=engine)
