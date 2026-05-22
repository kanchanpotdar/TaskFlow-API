import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ------------------------------------------------------------
# Get DATABASE URL (PostgreSQL on Render OR SQLite locally)
# ------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

# Fix for Render (sometimes gives "postgres://", SQLAlchemy needs "postgresql://")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# ------------------------------------------------------------
# Create engine
# ------------------------------------------------------------

if DATABASE_URL.startswith("sqlite"):
    # Local development
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL (Render)
    engine = create_engine(DATABASE_URL)


# ------------------------------------------------------------
# Session
# ------------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ------------------------------------------------------------
# Dependency
# ------------------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
