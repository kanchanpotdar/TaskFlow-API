# TaskFlow API

TaskFlow API is a FastAPI-based task management system with a Streamlit dashboard.

## Features

- Create tasks
- View all tasks
- Edit tasks
- Delete tasks
- Mark tasks as completed
- Reopen completed tasks
- Filter by priority
- Sort tasks
- Search tasks
- Track overdue tasks
- View task statistics

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Streamlit
- Uvicorn
- Requests
- Pandas

## Project Structure

```text
task_manager/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── routes.py
│
├── streamlit_app.py
├── requirements.txt
└── README.md