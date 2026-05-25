# Import database session type.
from sqlalchemy.orm import Session

# Import date for overdue logic.
from datetime import date

# Import Optional for optional filters.
from typing import Optional

# Import models and schemas.
from app import models, schemas


# Create one new task.
def create_task(db: Session, task: schemas.TaskCreate):
    # Convert Pydantic schema into dictionary.
    data = task.model_dump()

    # Set default category if category is missing or empty.
    if "category" not in data or not data["category"]:
        data["category"] = "Other"

    # Create SQLAlchemy Task object.
    new_task = models.Task(**data)

    # Add task to database session.
    db.add(new_task)

    # Save task in database.
    db.commit()

    # Refresh task to get generated values like ID and created_at.
    db.refresh(new_task)

    return new_task


# Get all tasks with optional filters and sorting.
def get_tasks(
    db: Session,
    priority: Optional[str] = None,
    sort_by: Optional[str] = None,
    category: Optional[str] = None
):
    # Start query from Task table.
    query = db.query(models.Task)

    # Filter by priority if provided.
    if priority:
        query = query.filter(models.Task.priority == priority)

    # Filter by category if provided.
    if category:
        query = query.filter(models.Task.category == category)

    # Sort by due date.
    if sort_by == "due_date":
        query = query.order_by(models.Task.due_date)

    # Sort by priority alphabetically.
    elif sort_by == "priority":
        query = query.order_by(models.Task.priority)

    # Sort by latest created task first.
    elif sort_by == "created_at":
        query = query.order_by(models.Task.created_at.desc())

    return query.all()


# Get one task by ID.
def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# Update a task by ID.
def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    # Find existing task.
    task = get_task(db, task_id)

    # Return None if task does not exist.
    if not task:
        return None

    # Convert only provided fields into dictionary.
    update_data = task_update.model_dump(exclude_unset=True)

    # Update task fields dynamically.
    for key, value in update_data.items():
        setattr(task, key, value)

    # Save changes.
    db.commit()

    # Refresh updated task.
    db.refresh(task)

    return task


# Delete a task by ID.
def delete_task(db: Session, task_id: int):
    # Find task.
    task = get_task(db, task_id)

    # Return None if task does not exist.
    if not task:
        return None

    # Delete task from database.
    db.delete(task)

    # Save deletion.
    db.commit()

    return task


# Search tasks by title keyword.
def search_tasks(db: Session, keyword: str):
    return db.query(models.Task).filter(
        models.Task.title.contains(keyword)
    ).all()


# Get overdue pending tasks.
def get_overdue_tasks(db: Session):
    today = date.today()

    return db.query(models.Task).filter(
        models.Task.due_date < today,
        models.Task.completed == False
    ).all()


# Get task statistics for dashboard.
def get_stats(db: Session):
    # Count all tasks.
    total_tasks = db.query(models.Task).count()

    # Count completed tasks.
    completed = db.query(models.Task).filter(
        models.Task.completed == True
    ).count()

    # Count pending tasks.
    pending = db.query(models.Task).filter(
        models.Task.completed == False
    ).count()

    # Count overdue pending tasks.
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


# Create multiple tasks at once.
def create_tasks_bulk(db: Session, tasks: list[schemas.TaskCreate]):
    # Store new task objects.
    new_tasks = []

    # Convert each incoming task into SQLAlchemy model.
    for task in tasks:
        data = task.model_dump()

        # Set default category if missing.
        if "category" not in data or not data["category"]:
            data["category"] = "Other"

        # Create task object.
        new_task = models.Task(**data)

        # Add to list.
        new_tasks.append(new_task)

    # Add all tasks to database session.
    db.add_all(new_tasks)

    # Save all tasks.
    db.commit()

    # Refresh each task to get generated IDs.
    for task in new_tasks:
        db.refresh(task)

    return new_tasks