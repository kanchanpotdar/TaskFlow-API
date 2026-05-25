# Import FastAPI.
from fastapi import FastAPI

# Import text for raw SQL migration query.
from sqlalchemy import text

# Import database engine, Base, and database URL.
from app.database import engine, Base, DATABASE_URL

# Import API router.
from app.routes import router


# Create database tables if they do not exist.
# This works for first-time table creation.
Base.metadata.create_all(bind=engine)


# Temporary PostgreSQL migration.
# This is useful if the tasks table already exists without the category column.
# For proper production projects, use Alembic migrations later.
if DATABASE_URL.startswith("postgresql"):
    with engine.begin() as connection:
        # Add category column if it does not already exist.
        connection.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'Other'"
            )
        )

        # Fill missing category values with Other.
        connection.execute(
            text(
                "UPDATE tasks "
                "SET category = 'Other' "
                "WHERE category IS NULL"
            )
        )


# Create FastAPI application.
app = FastAPI(
    title="TaskFlow API",
    description="A FastAPI-based task and productivity management backend",
    version="1.1.0"
)


# Include routes from routes.py.
app.include_router(router)


# Home endpoint to check if backend is running.
@app.get("/")
def home():
    return {
        "message": "Welcome to TaskFlow API"
    }