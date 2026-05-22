# TaskFlow API

TaskFlow API is a full-stack task management application built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Pydantic**, and **Streamlit**.

The project provides a backend API for managing tasks and a Streamlit dashboard for interacting with the system visually. Users can create, view, update, delete, filter, search, and track tasks. Version **1.2.0** includes task categories and dashboard analytics.

---

## Version

```text
v1.2.0
```

---

## Live Demo

### Backend API Documentation

```text
https://taskflow-api-st4d.onrender.com/docs
```

### Frontend Dashboard

```text
https://taskflow-api-cezqtvdx8bu4qyy7d4xbw3.streamlit.app/
```

### GitHub Repository

```text
https://github.com/kanchanpotdar/TaskFlow-API
```

### Version 1.2.0 Code

```text
https://github.com/kanchanpotdar/TaskFlow-API/tree/v1.2.0
```

---

## Project Overview

TaskFlow API is a productivity management system where users can manage daily tasks through a backend API and a frontend dashboard.

The application allows users to:

- Create new tasks
- View all tasks
- Edit existing tasks
- Delete tasks
- Mark tasks as completed
- Reopen completed tasks
- Assign priority levels
- Assign categories
- Track due dates
- Detect overdue tasks
- Search tasks by title
- Filter tasks by priority
- Filter tasks by category
- Sort tasks by due date, priority, or creation date
- View task statistics
- View dashboard charts and insights

---

## Key Features

### 1. Task Management

Each task contains the following fields:

```text
Title
Description
Priority
Category
Due Date
Completion Status
Creation Date
```

Supported priorities:

```text
High
Medium
Low
```

Supported categories:

```text
Work
College
Personal
Other
```

---

### 2. CRUD Operations

The backend supports full CRUD functionality:

```text
Create Task
Read All Tasks
Read Single Task
Update Task
Delete Task
```

---

### 3. Filtering

Users can filter tasks by priority and category.

Example API requests:

```text
GET /tasks?priority=High
GET /tasks?category=Work
GET /tasks?priority=High&category=Work
```

---

### 4. Sorting

Users can sort tasks by:

```text
Due Date
Priority
Created Date
```

Example:

```text
GET /tasks?sort_by=due_date
```

---

### 5. Search

Users can search tasks by keyword in the task title.

Example:

```text
GET /tasks/search?keyword=api
```

---

### 6. Overdue Task Tracking

The application detects overdue tasks using this logic:

```text
due_date < today
AND
completed == False
```

Endpoint:

```text
GET /tasks/overdue
```

---

### 7. Statistics

The statistics endpoint returns:

```text
Total Tasks
Completed Tasks
Pending Tasks
Overdue Tasks
```

Endpoint:

```text
GET /stats
```

Sample response:

```json
{
  "total_tasks": 10,
  "completed": 4,
  "pending": 6,
  "overdue": 2
}
```

---

### 8. Dashboard Analytics

The Streamlit dashboard includes visual insights such as:

```text
Tasks by Category
Tasks by Priority
Completion Status
Pending Tasks by Category
```

---

## Tech Stack

### Backend

- **FastAPI** — used to build the REST API backend
- **Uvicorn** — used to run the FastAPI server
- **SQLAlchemy** — used as the ORM for database operations
- **Pydantic** — used for request and response validation

### Database

- **PostgreSQL** — used as the cloud database for persistent task storage
- **SQLite** — used as a local fallback database during development

### Frontend

- **Streamlit** — used to build the interactive frontend dashboard
- **Requests** — used by Streamlit to call FastAPI backend APIs
- **Pandas** — used to display task data and generate dashboard analytics

### Deployment

- **Render** — used to deploy the FastAPI backend and PostgreSQL database
- **Streamlit Community Cloud** — used to deploy the Streamlit frontend dashboard
- **GitHub** — used for source code management and version control

---

## Project Structure

```text
task_manager/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── routes.py
│
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .gitignore
└── tasks.db
```

Note:

```text
tasks.db is used only for local SQLite development.
On Render, the application uses PostgreSQL through the DATABASE_URL environment variable.
```

---

## File-by-File Explanation

### `app/database.py`

This file manages the database connection.

It does the following:

- Reads the database URL from the environment variable `DATABASE_URL`
- Uses PostgreSQL on Render
- Falls back to SQLite locally if `DATABASE_URL` is not available
- Creates the SQLAlchemy engine
- Creates database sessions
- Provides the `get_db()` dependency for FastAPI routes

Main responsibility:

```text
Connect the application to the database safely.
```

---

### `app/models.py`

This file defines the database table structure.

It contains the `Task` model, which becomes the `tasks` table in the database.

Task table fields:

```text
id
title
description
priority
category
due_date
completed
created_at
```

Main responsibility:

```text
Define how task data is stored in the database.
```

---

### `app/schemas.py`

This file defines validation schemas using Pydantic.

It contains:

```text
TaskCreate
TaskUpdate
TaskResponse
```

Purpose of each schema:

```text
TaskCreate   → Validates data while creating a task
TaskUpdate   → Validates optional fields while updating a task
TaskResponse → Controls how task data is returned by the API
```

Main responsibility:

```text
Validate incoming API data and structure outgoing API responses.
```

---

### `app/crud.py`

This file contains database operation logic.

It includes functions for:

```text
create_task()
get_tasks()
get_task()
update_task()
delete_task()
search_tasks()
get_overdue_tasks()
get_stats()
```

Main responsibility:

```text
Perform actual database operations.
```

This file separates business logic from API routes, making the backend cleaner and easier to maintain.

---

### `app/routes.py`

This file defines all API endpoints.

Main endpoints:

```text
POST   /tasks
GET    /tasks
GET    /tasks/search
GET    /tasks/overdue
GET    /stats
GET    /tasks/{task_id}
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

Main responsibility:

```text
Receive API requests and call the correct CRUD functions.
```

---

### `app/main.py`

This is the main entry point of the FastAPI application.

It does the following:

- Creates database tables
- Runs a temporary migration to ensure the `category` column exists in PostgreSQL
- Creates the FastAPI app object
- Includes the API router
- Provides a home route for health checking

Main responsibility:

```text
Start and configure the FastAPI backend application.
```

---

### `streamlit_app.py`

This file contains the frontend dashboard.

It does not connect directly to the database.

Instead, it calls the FastAPI backend using HTTP requests.

The dashboard supports:

```text
Create Task
View Tasks
Edit Task
Delete Task
Mark Task Completed
Reopen Task
Filter by Priority
Filter by Category
Search Tasks
View Overdue Tasks
View Statistics
View Charts
```

Main responsibility:

```text
Provide a user-friendly interface for interacting with the backend APIs.
```

---

### `requirements.txt`

This file contains all Python dependencies required to run the project.

Main packages include:

```text
fastapi
uvicorn
sqlalchemy
pydantic
psycopg2-binary
streamlit
requests
pandas
```

Main responsibility:

```text
Allow the project environment to be recreated easily.
```

---

### `.gitignore`

This file prevents unnecessary or sensitive files from being uploaded to GitHub.

Common ignored files:

```text
venv/
__pycache__/
*.pyc
.env
tasks.db
.streamlit/
.vscode/
```

Main responsibility:

```text
Keep the repository clean and secure.
```

---

## API Endpoints

### Home

```text
GET /
```

Returns a welcome message.

---

### Create Task

```text
POST /tasks
```

Sample request:

```json
{
  "title": "Learn FastAPI",
  "description": "Practice REST API development",
  "priority": "High",
  "category": "Work",
  "due_date": "2026-05-25"
}
```

---

### Get All Tasks

```text
GET /tasks
```

Returns all tasks.

---

### Filter Tasks by Priority

```text
GET /tasks?priority=High
```

---

### Filter Tasks by Category

```text
GET /tasks?category=College
```

---

### Filter by Priority and Category

```text
GET /tasks?priority=High&category=Work
```

---

### Sort Tasks

```text
GET /tasks?sort_by=due_date
GET /tasks?sort_by=priority
GET /tasks?sort_by=created_at
```

---

### Search Tasks

```text
GET /tasks/search?keyword=api
```

---

### Get Overdue Tasks

```text
GET /tasks/overdue
```

---

### Get Statistics

```text
GET /stats
```

Sample response:

```json
{
  "total_tasks": 10,
  "completed": 4,
  "pending": 6,
  "overdue": 2
}
```

---

### Get Single Task

```text
GET /tasks/{task_id}
```

---

### Update Task

```text
PUT /tasks/{task_id}
```

Sample request:

```json
{
  "title": "Updated task title",
  "priority": "Medium",
  "category": "Personal",
  "completed": true
}
```

---

### Delete Task

```text
DELETE /tasks/{task_id}
```

---

## How the Application Works

### End-to-End Flow

```text
User opens Streamlit dashboard
        ↓
User creates or updates a task
        ↓
Streamlit sends an HTTP request to FastAPI
        ↓
FastAPI validates the data using Pydantic schemas
        ↓
Routes call CRUD functions
        ↓
CRUD functions interact with PostgreSQL using SQLAlchemy
        ↓
PostgreSQL stores or returns task data
        ↓
FastAPI sends JSON response back to Streamlit
        ↓
Streamlit updates the dashboard
```

---

## Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/kanchanpotdar/TaskFlow-API.git
cd TaskFlow-API
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

---

### 3. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Run FastAPI Backend

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 6. Run Streamlit Frontend

Open a second terminal and run:

```bash
streamlit run streamlit_app.py
```

Frontend runs at:

```text
http://localhost:8501
```

---

## Deployment Details

### Backend Deployment

The FastAPI backend is deployed on Render.

Render start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

### Database Deployment

The production database is PostgreSQL on Render.

The app reads the PostgreSQL connection string from:

```text
DATABASE_URL
```

This value is stored as an environment variable in Render and is not hardcoded in the source code.

---

### Frontend Deployment

The Streamlit dashboard is deployed on Streamlit Community Cloud.

The deployed frontend calls the Render backend API.

---

## Version History

### v1.2.0

Current version.

Changes:

```text
Added task categories
Added category filtering
Added PostgreSQL support
Added dashboard analytics
Added task insights by category and priority
Improved Streamlit dashboard
Added persistent cloud database storage
```

---

### v1.0.0

Initial stable version.

Features:

```text
FastAPI backend
SQLite database
Task CRUD operations
Priority support
Due date tracking
Overdue task detection
Stats endpoint
Streamlit dashboard
```

---

## Concepts Demonstrated

This project demonstrates:

```text
REST API development
Backend architecture
Database modeling
ORM usage
Request validation
Response validation
CRUD operations
Query parameters
Filtering
Sorting
Searching
Cloud database integration
Frontend-backend integration
Dashboard analytics
Deployment
Version control
Git tags
```

---

## Future Improvements

Possible next upgrades:

```text
User login and authentication
Separate tasks per user
Task status: Pending, In Progress, Completed
Task reminders
Email notifications
Calendar view
Export tasks to CSV
Dark mode UI
Docker setup
Automated tests
Pagination
Role-based access
```

---

## Author

```text
Kanchan Potdar
```

---

## Project Status

```text
Active development
Current stable version: v1.2.0
```