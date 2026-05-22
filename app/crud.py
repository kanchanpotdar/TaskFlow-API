# Session is the active connection to the database
from sqlalchemy.orm import Session

# date is used to check overdue tasks
from datetime import date

# Import database model and validation schemas
from app import models, schemas

from typing import Optional


# ------------------------------------------------------------
# CREATE TASK
# ------------------------------------------------------------
def create_task(db: Session, task: schemas.TaskCreate):

    # Convert schema → dict
    data = task.model_dump()

    # Ensure category exists
    if "category" not in data or not data["category"]:
        data["category"] = "Other"

    # Create task
    new_task = models.Task(**data)

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# ------------------------------------------------------------
# GET ALL TASKS
# ------------------------------------------------------------
def get_tasks(
    db: Session,
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    category: Optional[str] = None
):
    query = db.query(models.Task)

    # Filter by priority
    if priority:
        query = query.filter(models.Task.priority == priority)

    # ✅ NEW: Filter by category
    if category:
        query = query.filter(models.Task.category == category)

    # Sorting
    if sort_by == "due_date":
        query = query.order_by(models.Task.due_date)

    elif sort_by == "priority":
        query = query.order_by(models.Task.priority)

    elif sort_by == "created_at":
        query = query.order_by(models.Task.created_at.desc())

    return query.all()


# ------------------------------------------------------------
# GET SINGLE TASK
# ------------------------------------------------------------
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# ------------------------------------------------------------
# UPDATE TASK
# ------------------------------------------------------------
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):

    task = get_task(db, task_id)

    if not task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)

    # ✅ Works automatically for category too
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


# ------------------------------------------------------------
# DELETE TASK
# ------------------------------------------------------------
def delete_task(db: Session, task_id: int):

    task = get_task(db, task_id)

    if not task:
        return None

    db.delete(task)
    db.commit()

    return task


# ------------------------------------------------------------
# SEARCH TASKS
# ------------------------------------------------------------
def search_tasks(db: Session, keyword: str):

    return db.query(models.Task).filter(
        models.Task.title.contains(keyword)
    ).all()


# ------------------------------------------------------------
# GET OVERDUE TASKS
# ------------------------------------------------------------
def get_overdue_tasks(db: Session):

    today = date.today()

    return db.query(models.Task).filter(
        models.Task.due_date < today,
        models.Task.completed == False
    ).all()


# ------------------------------------------------------------
# GET STATISTICS
# ------------------------------------------------------------
def get_stats(db: Session):

    total_tasks = db.query(models.Task).count()

    completed = db.query(models.Task).filter(
        models.Task.completed == True
    ).count()

    pending = db.query(models.Task).filter(
        models.Task.completed == False
    ).count()

    overdue = db.query(models.Task).filter(
        models.Task.due_date < date.today(),
        models.Task.completed == False
    ).count()

    return {
        "total_tasks": total_tasks,
        "completed": completed,
        "pending": pending,
        "overdue": overdue
    }


"""
Flow:

User → FastAPI → Schema validation → routes.py → crud.py → PostgreSQL → response

Now includes:
 category support
 filtering by category
 persistent database (PostgreSQL)
"""