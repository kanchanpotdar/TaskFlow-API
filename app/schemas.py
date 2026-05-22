from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str
    category: str = "Other"
    due_date: date


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    category: str
    due_date: date
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True