# Import operating system module to read environment variables.
import os

# Import SQLAlchemy tools for database connection and session handling.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Read database URL from environment variable.
# On Render, DATABASE_URL will point to PostgreSQL.
# Locally, if DATABASE_URL is missing, SQLite will be used as fallback.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")


# Render sometimes provides PostgreSQL URLs starting with postgres://.
# SQLAlchemy expects postgresql://, so this converts it safely.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Create database engine.
# SQLite needs check_same_thread=False.
# PostgreSQL does not need this setting.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)


# Create database session factory.
# Each API request will get a database session from this.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for all SQLAlchemy models.
Base = declarative_base()


# Dependency function used by FastAPI routes.
# It opens a database session and closes it after request completion.
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()