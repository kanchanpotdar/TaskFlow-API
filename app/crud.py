# Session is the active connection to the database
from sqlalchemy.orm import Session

# date is used to check overdue tasks
from datetime import date

# Import database model and validation schemas
from app import models, schemas

from typing import Optional
# CREATE TASK
# This function inserts a new task into the database.
def create_task(db: Session, task: schemas.TaskCreate):

    # Convert Pydantic schema into dictionary using model_dump()
    # Then unpack it into Task model using **.
    #
    # Example:
    # task.model_dump() becomes:
    # {
    #   "title": "Solve DP",
    #   "description": "Practice memoization",
    #   "priority": "High",
    #   "due_date": "2026-05-25"
    # }
    new_task = models.Task(**task.model_dump())

    # Add the new task object to the database session
    db.add(new_task)

    # Save the change permanently in the database
    db.commit()

    # Refresh the object so it gets generated fields like id and created_at
    db.refresh(new_task)

    # Return the newly created task
    return new_task


# GET ALL TASKS
# This function fetches tasks.
# It also supports optional filtering by priority and sorting.
def get_tasks(db: Session, priority: Optional[str] = None, sort_by: Optional[str] = None):

    # Start a database query on the Task table
    query = db.query(models.Task)

    # If priority is provided, filter tasks by priority
    # Example: /tasks?priority=High
    if priority:
        query = query.filter(models.Task.priority == priority)

    # Sort tasks based on selected field
    # Example: /tasks?sort_by=due_date
    if sort_by == "due_date":
        query = query.order_by(models.Task.due_date)

    elif sort_by == "priority":
        query = query.order_by(models.Task.priority)

    elif sort_by == "created_at":
        query = query.order_by(models.Task.created_at.desc())

    # Execute the query and return all matching records
    return query.all()


# GET SINGLE TASK
# This function fetches one task using task ID.
def get_task(db: Session, task_id: int):

    # Find first task where id matches task_id
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# UPDATE TASK
# This function updates an existing task.
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):

    # First check if task exists
    task = get_task(db, task_id)

    # If task does not exist, return None
    if not task:
        return None

    # Convert update data into dictionary.
    # exclude_unset=True means only fields sent by user will be updated.
    #
    # Example:
    # If user sends only {"completed": true},
    # only completed will be updated.
    update_data = task_update.model_dump(exclude_unset=True)

    # Loop through each field and update the task object
    for key, value in update_data.items():
        setattr(task, key, value)

    # Save changes permanently
    db.commit()

    # Refresh updated task from database
    db.refresh(task)

    # Return updated task
    return task


# DELETE TASK
# This function deletes a task from the database.
def delete_task(db: Session, task_id: int):

    # First check if task exists
    task = get_task(db, task_id)

    # If task does not exist, return None
    if not task:
        return None

    # Delete task from database session
    db.delete(task)

    # Save deletion permanently
    db.commit()

    # Return deleted task object
    return task


# SEARCH TASKS
# This function searches tasks by title keyword.
def search_tasks(db: Session, keyword: str):

    # contains() checks if title contains the keyword
    # Example:
    # keyword = "graph"
    # It will match "Study graph algorithms"
    return db.query(models.Task).filter(
        models.Task.title.contains(keyword)
    ).all()


# GET OVERDUE TASKS
# This function returns tasks whose due date has passed and are not completed.
def get_overdue_tasks(db: Session):

    # Get today's date
    today = date.today()

    # Return tasks where due_date is before today and completed is False
    return db.query(models.Task).filter(
        models.Task.due_date < today,
        models.Task.completed == False
    ).all()


# GET STATISTICS
# This function returns total, completed, pending, and overdue task counts.
def get_stats(db: Session):

    # Count all tasks
    total_tasks = db.query(models.Task).count()

    # Count completed tasks
    completed = db.query(models.Task).filter(
        models.Task.completed == True
    ).count()

    # Count pending tasks
    pending = db.query(models.Task).filter(
        models.Task.completed == False
    ).count()

    # Count overdue tasks
    overdue = db.query(models.Task).filter(
        models.Task.due_date < date.today(),
        models.Task.completed == False
    ).count()

    # Return result as a dictionary
    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "pending": pending,
        "overdue": overdue
    }

"""

User sends JSON
        ↓
FastAPI validates using TaskCreate schema
        ↓
routes.py receives request
        ↓
crud.py creates database record
        ↓
SQLite stores the task
        ↓
API returns created task

"""