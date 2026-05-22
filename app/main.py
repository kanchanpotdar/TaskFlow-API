from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine, Base, DATABASE_URL
from app.routes import router


Base.metadata.create_all(bind=engine)


# Temporary migration:
# If tasks table already exists without category,
# this safely adds category to PostgreSQL.
if DATABASE_URL.startswith("postgresql"):
    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS category VARCHAR DEFAULT 'Other'"
            )
        )

        connection.execute(
            text(
                "UPDATE tasks "
                "SET category = 'Other' "
                "WHERE category IS NULL"
            )
        )


app = FastAPI(
    title="TaskFlow API",
    description="A FastAPI-based task and productivity management backend",
    version="1.1.0"
)


app.include_router(router)


@app.get("/")
def home():
    return {
        "message": "Welcome to TaskFlow API"
    }