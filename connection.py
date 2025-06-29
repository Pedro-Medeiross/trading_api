import os
import logging
from typing import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Database connection configuration
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Construct database URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with connection pooling
# Using QueuePool with optimized defaults for a web application
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,  # Increased number of connections for better concurrency
    max_overflow=20,  # Increased max overflow for handling traffic spikes
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connections before using them
    echo=False  # Set to True for SQL query logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Create a new database session and close it when done.

    This dependency is used in FastAPI route functions to get a database session.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions.

    This is useful for scripts and background tasks that need database access
    outside of the FastAPI request lifecycle.

    Usage:
        with get_db_context() as db:
            db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
