# Import Pydantic BaseModel for request and response validation.
from pydantic import BaseModel

# Import date and datetime types.
from datetime import date, datetime

# Import Optional for fields that may be empty.
from typing import Optional


# Schema used when creating a new task.
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    category: str = "Other"
    due_date: date


# Schema used when updating an existing task.
# All fields are optional because user may update only one field.
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


# Schema used when sending task data back to frontend.
class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    category: str
    due_date: date
    completed: bool
    created_at: datetime

    # Allows Pydantic to read data from SQLAlchemy model objects.
    class Config:
        from_attributes = True