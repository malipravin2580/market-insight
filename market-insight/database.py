from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@localhost:5432/fast_api_marketinsights"

# Create engine and session factory
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)
