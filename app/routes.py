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


# Create router object
router = APIRouter()


# ------------------------------------------------------------
# CREATE TASK API
# ------------------------------------------------------------
@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


# ------------------------------------------------------------
# GET ALL TASKS API
# ------------------------------------------------------------
@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    category: Optional[str] = None,   # ✅ NEW
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, priority, sort_by, category)


# ------------------------------------------------------------
# SEARCH TASKS API
# ------------------------------------------------------------
@router.get("/tasks/search", response_model=List[schemas.TaskResponse])
def search_tasks(keyword: str, db: Session = Depends(get_db)):
    return crud.search_tasks(db, keyword)


# ------------------------------------------------------------
# OVERDUE TASKS API
# ------------------------------------------------------------
@router.get("/tasks/overdue", response_model=List[schemas.TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):
    return crud.get_overdue_tasks(db)


# ------------------------------------------------------------
# STATS API
# ------------------------------------------------------------
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


# ------------------------------------------------------------
# GET SINGLE TASK API
# ------------------------------------------------------------
@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):

    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


# ------------------------------------------------------------
# UPDATE TASK API
# ------------------------------------------------------------
@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: Session = Depends(get_db)
):

    task = crud.update_task(db, task_id, task_update)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


# ------------------------------------------------------------
# DELETE TASK API
# ------------------------------------------------------------
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):

    task = crud.delete_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "message": "Task deleted successfully"
    }
