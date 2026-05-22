# APIRouter helps organize API endpoints separately from main.py
# Depends is used for dependency injection
# HTTPException is used to return proper error messages
from fastapi import APIRouter, Depends, HTTPException

# Session is the database session type
from sqlalchemy.orm import Session

# List and Optional are used for type hints
from typing import List, Optional

# Import schemas for request and response validation
# Import crud for database operations
from app import schemas, crud

# Import get_db to get database session
from app.database import get_db


# Create router object.
# All endpoints will be attached to this router.
router = APIRouter()


# CREATE TASK API
# Method: POST
# URL: /tasks
# Purpose: Create a new task
@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):

    # Pass validated task data to crud function
    return crud.create_task(db, task)


# GET ALL TASKS API
# Method: GET
# URL: /tasks
# Purpose: Fetch all tasks
# Optional query parameters:
# /tasks?priority=High
# /tasks?sort_by=due_date
@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):

    # Fetch tasks from database using optional filters
    return crud.get_tasks(db, priority, sort_by)


# SEARCH TASKS API
# Method: GET
# URL: /tasks/search?keyword=graph
# Purpose: Search tasks by title

# Important:
# This route must be written before /tasks/{task_id}
# Otherwise FastAPI may think "search" is a task_id.
@router.get("/tasks/search", response_model = List[schemas.TaskResponse])
def search_tasks(keyword: str, db: Session = Depends(get_db)):

    # Search tasks using keyword
    return crud.search_tasks(db, keyword)


# OVERDUE TASKS API
# Method: GET
# URL: /tasks/overdue
# Purpose: Get all overdue pending tasks
#
# Important:
# This route must also be before /tasks/{task_id}
@router.get("/tasks/overdue", response_model=List[schemas.TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):

    # Return overdue tasks
    return crud.get_overdue_tasks(db)


# STATS API
# Method: GET
# URL: /stats
# Purpose: Return task statistics
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    # Return total, completed, pending, overdue counts
    return crud.get_stats(db)


# GET SINGLE TASK API
# Method: GET
# URL: /tasks/{task_id}
# Purpose: Fetch one task by ID
@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):

    # Try to find task
    task = crud.get_task(db, task_id)

    # If task not found, return 404 error
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return found task
    return task


# UPDATE TASK API
# Method: PUT
# URL: /tasks/{task_id}
# Purpose: Update existing task
@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):

    # Try to update task
    task = crud.update_task(db, task_id, task_update)

    # If task not found, return 404 error
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return updated task
    return task


# DELETE TASK API
# Method: DELETE
# URL: /tasks/{task_id}
# Purpose: Delete task by ID
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):

    # Try to delete task
    task = crud.delete_task(db, task_id)

    # If task not found, return 404 error
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return success message
    return {
        "message": "Task deleted successfully"
    }