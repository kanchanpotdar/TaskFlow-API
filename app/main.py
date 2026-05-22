# Import FastAPI class
from fastapi import FastAPI

# Import engine and Base for database table creation
from app.database import engine, Base

# Import router that contains all API endpoints
from app.routes import router


# Create all database tables.
# SQLAlchemy checks models.py and creates tables if they do not exist.
Base.metadata.create_all(bind=engine)


# Create FastAPI application object.
# This object represents the entire backend application.
app = FastAPI(
    title="TaskFlow API",
    description="A FastAPI-based task and productivity management backend",
    version="1.0.0"
)


# Connect routes.py with main FastAPI app.
# Without this, your API endpoints will not work.
app.include_router(router)


# Home route.
# Useful to quickly check if backend is running.
@app.get("/")
def home():
    return {
        "message": "Welcome to TaskFlow API"
    }
