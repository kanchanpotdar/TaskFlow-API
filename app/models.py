# Import SQLAlchemy column types.
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime

# Import datetime to set default task creation time.
from datetime import datetime

# Import Base from database.py.
from app.database import Base


# Task model maps to the tasks table in the database.
class Task(Base):
    __tablename__ = "tasks"

    # Unique task ID.
    id = Column(Integer, primary_key=True, index=True)

    # Task title is required.
    title = Column(String, nullable=False)

    # Task description is optional.
    description = Column(String, nullable=True)

    # Task priority is required.
    priority = Column(String, nullable=False)

    # Task category is required and defaults to Other.
    category = Column(String, nullable=False, default="Other")

    # Due date is required.
    due_date = Column(Date, nullable=False)

    # Completed status defaults to False.
    completed = Column(Boolean, default=False)

    # Task creation timestamp.
    created_at = Column(DateTime, default=datetime.utcnow)