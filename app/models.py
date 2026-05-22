from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from datetime import datetime
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

"""
tasks
│
├── id
├── title
├── description
├── priority
├── due_date
├── completed
└── created_at

"""