# Import FastAPI routing tools.
from fastapi import APIRouter, Depends, HTTPException

# Import database session.
from sqlalchemy.orm import Session

# Import typing tools.
from typing import List, Optional

# Import project schemas and CRUD functions.
from app import schemas, crud

# Import database dependency.
from app.database import get_db


# Create router object.
router = APIRouter()


# Create one task.
@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


# Create multiple tasks at once.
@router.post("/tasks/bulk", response_model=List[schemas.TaskResponse])
def create_tasks_bulk(
    tasks: List[schemas.TaskCreate],
    db: Session = Depends(get_db)
):
    return crud.create_tasks_bulk(db, tasks)


# Get all tasks with optional filters.
@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, priority, sort_by, category)


# Search tasks by title keyword.
@router.get("/tasks/search", response_model=List[schemas.TaskResponse])
def search_tasks(keyword: str, db: Session = Depends(get_db)):
    return crud.search_tasks(db, keyword)


# Get overdue tasks.
@router.get("/tasks/overdue", response_model=List[schemas.TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):
    return crud.get_overdue_tasks(db)


# Get dashboard statistics.
@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


# Get one task by ID.
@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


# Update one task by ID.
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


# Delete one task by ID.
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "message": "Task deleted successfully"
    }