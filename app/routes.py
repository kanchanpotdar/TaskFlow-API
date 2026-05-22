from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, crud
from app.database import get_db


router = APIRouter()


@router.post("/tasks", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_tasks(
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, priority, sort_by, category)


@router.get("/tasks/search", response_model=List[schemas.TaskResponse])
def search_tasks(keyword: str, db: Session = Depends(get_db)):
    return crud.search_tasks(db, keyword)


@router.get("/tasks/overdue", response_model=List[schemas.TaskResponse])
def get_overdue_tasks(db: Session = Depends(get_db)):
    return crud.get_overdue_tasks(db)


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


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


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.delete_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "message": "Task deleted successfully"
    }