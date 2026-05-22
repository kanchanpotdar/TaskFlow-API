# BaseModel is used to create data validation models
from pydantic import BaseModel

# date is used for due_date
# datetime is used for created_at
from datetime import date, datetime

# Optional means a field is not compulsory
from typing import Optional


# This schema is used when creating a new task.
# The user must send title, priority, and due_date.
# Description is optional.
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    due_date: date


# This schema is used when updating a task.
# All fields are optional because the user may update only one field.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


# This schema is used when returning task data from the API.
# It defines how the API response should look.
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    due_date: date
    completed: bool
    created_at: datetime

    # This allows Pydantic to convert SQLAlchemy objects into response JSON.
    # Without this, FastAPI may not know how to return database model objects.
    class Config:
        from_attributes = True