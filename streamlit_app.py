# ------------------------------------------------------------
# Streamlit Frontend for TaskFlow API
# ------------------------------------------------------------
# This file creates the frontend dashboard.
# It does not directly connect to the database.
# It calls FastAPI backend APIs using the requests library.
# ------------------------------------------------------------

import streamlit as st
import requests
import pandas as pd
from datetime import date
import os

# ------------------------------------------------------------
# FastAPI Backend URL
# ------------------------------------------------------------
# Make sure your FastAPI backend is running first:
# uvicorn app.main:app --reload
# ------------------------------------------------------------

API_URL = st.secrets.get(
    "API_URL",
    os.getenv("API_URL", "http://127.0.0.1:8000")
)
"""
Locally → use http://127.0.0.1:8000
On Streamlit Cloud → use the deployed Render backend URL from secrets
"""

# ------------------------------------------------------------
# Streamlit Page Configuration
# ------------------------------------------------------------

st.set_page_config(
    page_title="TaskFlow Dashboard",
    layout="wide"
)


# ------------------------------------------------------------
# Helper Function for Safe Text Handling
# ------------------------------------------------------------

def safe_text(value):
    """
    Converts None into an empty string and removes extra spaces.
    This prevents errors like:
    'strip' is not a known attribute of None
    """
    return (value or "").strip()


# ------------------------------------------------------------
# API Helper Functions
# ------------------------------------------------------------

def check_backend():
    """
    Checks whether the FastAPI backend is running.
    """
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def get_tasks(params=None):
    """
    Calls GET /tasks API.
    Returns all tasks based on optional filters.
    """
    try:
        response = requests.get(
            f"{API_URL}/tasks",
            params=params,
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


def get_stats():
    """
    Calls GET /stats API.
    Returns total, completed, pending, and overdue task count.
    """
    default_stats = {
        "total_tasks": 0,
        "completed": 0,
        "pending": 0,
        "overdue": 0
    }

    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)

        if response.status_code == 200:
            return response.json()

        return default_stats

    except Exception:
        return default_stats


def get_overdue_tasks():
    """
    Calls GET /tasks/overdue API.
    Returns all overdue and incomplete tasks.
    """
    try:
        response = requests.get(f"{API_URL}/tasks/overdue", timeout=5)

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


def create_task(payload):
    """
    Calls POST /tasks API.
    Creates a new task.
    """
    try:
        response = requests.post(
            f"{API_URL}/tasks",
            json=payload,
            timeout=5
        )
        return response

    except Exception:
        return None


def update_task(task_id, payload):
    """
    Calls PUT /tasks/{task_id} API.
    Updates selected task.
    """
    try:
        response = requests.put(
            f"{API_URL}/tasks/{task_id}",
            json=payload,
            timeout=5
        )
        return response

    except Exception:
        return None


def delete_task(task_id):
    """
    Calls DELETE /tasks/{task_id} API.
    Deletes selected task.
    """
    try:
        response = requests.delete(
            f"{API_URL}/tasks/{task_id}",
            timeout=5
        )
        return response

    except Exception:
        return None


def search_tasks(keyword):
    """
    Calls GET /tasks/search API.
    Searches tasks by title keyword.
    """
    try:
        response = requests.get(
            f"{API_URL}/tasks/search",
            params={"keyword": keyword},
            timeout=5
        )

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


# ------------------------------------------------------------
# Page Header
# ------------------------------------------------------------

st.title("TaskFlow Dashboard")

st.write(
    "A simple productivity dashboard connected to a FastAPI backend."
)


# ------------------------------------------------------------
# Backend Status Check
# ------------------------------------------------------------

backend_running = check_backend()

if backend_running:
    st.success("Backend is running successfully.")
else:
    st.error(
        "Backend is not running. Please start FastAPI first using: "
        "`uvicorn app.main:app --reload`"
    )
    st.stop()


# ------------------------------------------------------------
# Sidebar: Create New Task
# ------------------------------------------------------------

st.sidebar.header("Create New Task")

title = st.sidebar.text_input("Task Title")

description = st.sidebar.text_area("Description")

priority_options = ["High", "Medium", "Low"]

priority = st.sidebar.selectbox(
    "Priority",
    priority_options
)

due_date = st.sidebar.date_input(
    "Due Date",
    min_value=date.today()
)

if st.sidebar.button("Create Task"):
    clean_title = safe_text(title)
    clean_description = safe_text(description)

    if not clean_title:
        st.sidebar.warning("Task title is required.")
    else:
        payload = {
            "title": clean_title,
            "description": clean_description,
            "priority": priority,
            "due_date": str(due_date)
        }

        response = create_task(payload)

        if response is not None and response.status_code in [200, 201]:
            st.sidebar.success("Task created successfully.")
            st.rerun()
        else:
            st.sidebar.error("Failed to create task.")


# ------------------------------------------------------------
# Statistics Section
# ------------------------------------------------------------

st.subheader("Task Statistics")

stats = get_stats()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tasks", stats.get("total_tasks", 0))
col2.metric("Completed", stats.get("completed", 0))
col3.metric("Pending", stats.get("pending", 0))
col4.metric("Overdue", stats.get("overdue", 0))


# ------------------------------------------------------------
# Filters Section
# ------------------------------------------------------------

st.subheader("Filters")

filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_priority = st.selectbox(
        "Filter by Priority",
        ["All", "High", "Medium", "Low"]
    )

with filter_col2:
    sort_by = st.selectbox(
        "Sort By",
        ["None", "due_date", "priority", "created_at"]
    )


# Prepare query parameters for GET /tasks
params = {}

if selected_priority != "All":
    params["priority"] = selected_priority

if sort_by != "None":
    params["sort_by"] = sort_by


# ------------------------------------------------------------
# All Tasks Section
# ------------------------------------------------------------

st.subheader("All Tasks")

tasks = get_tasks(params=params)

if tasks:
    df = pd.DataFrame(tasks)

    display_columns = [
        "id",
        "title",
        "description",
        "priority",
        "due_date",
        "completed",
        "created_at"
    ]

    existing_columns = [
        column for column in display_columns if column in df.columns
    ]

    df = df[existing_columns]

    st.dataframe(df, use_container_width=True)

else:
    st.info("No tasks found.")


# ------------------------------------------------------------
# Task Actions Section
# ------------------------------------------------------------

if tasks:
    st.subheader("Task Actions")

    task_ids = [task["id"] for task in tasks]

    selected_task_id = st.selectbox(
        "Select Task ID",
        task_ids
    )

    selected_task = None

    for task in tasks:
        if task["id"] == selected_task_id:
            selected_task = task
            break

    if selected_task is not None:
        action_tab1, action_tab2, action_tab3, action_tab4 = st.tabs(
            [
                "Edit Task",
                "Mark Completed",
                "Reopen Task",
                "Delete Task"
            ]
        )

        # ----------------------------------------------------
        # Edit Task
        # ----------------------------------------------------

        with action_tab1:
            st.write("Edit selected task details.")

            edited_title = st.text_input(
                "Edit Title",
                value=selected_task.get("title", "")
            )

            edited_description = st.text_area(
                "Edit Description",
                value=selected_task.get("description") or ""
            )

            current_priority = selected_task.get("priority", "Medium")

            if current_priority in priority_options:
                priority_index = priority_options.index(current_priority)
            else:
                priority_index = 1

            edited_priority = st.selectbox(
                "Edit Priority",
                priority_options,
                index=priority_index
            )

            edited_due_date = st.date_input(
                "Edit Due Date",
                value=pd.to_datetime(
                    selected_task.get("due_date", date.today())
                ).date()
            )

            edited_completed = st.checkbox(
                "Completed",
                value=bool(selected_task.get("completed", False))
            )

            if st.button("Save Changes"):
                clean_edited_title = safe_text(edited_title)
                clean_edited_description = safe_text(edited_description)

                if not clean_edited_title:
                    st.warning("Task title cannot be empty.")
                else:
                    update_payload = {
                        "title": clean_edited_title,
                        "description": clean_edited_description,
                        "priority": edited_priority,
                        "due_date": str(edited_due_date),
                        "completed": edited_completed
                    }

                    response = update_task(
                        selected_task_id,
                        update_payload
                    )

                    if response is not None and response.status_code == 200:
                        st.success("Task updated successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to update task.")

        # ----------------------------------------------------
        # Mark Task as Completed
        # ----------------------------------------------------

        with action_tab2:
            st.write("Mark the selected task as completed.")

            if bool(selected_task.get("completed", False)):
                st.info("This task is already completed.")
            else:
                if st.button("Mark as Completed"):
                    update_payload = {
                        "completed": True
                    }

                    response = update_task(
                        selected_task_id,
                        update_payload
                    )

                    if response is not None and response.status_code == 200:
                        st.success("Task marked as completed.")
                        st.rerun()
                    else:
                        st.error("Failed to mark task as completed.")

        # ----------------------------------------------------
        # Reopen Task
        # ----------------------------------------------------

        with action_tab3:
            st.write("Reopen a completed task and mark it as pending again.")

            if not bool(selected_task.get("completed", False)):
                st.info("This task is already pending.")
            else:
                if st.button("Reopen Task"):
                    update_payload = {
                        "completed": False
                    }

                    response = update_task(
                        selected_task_id,
                        update_payload
                    )

                    if response is not None and response.status_code == 200:
                        st.success("Task reopened successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to reopen task.")

        # ----------------------------------------------------
        # Delete Task
        # ----------------------------------------------------

        with action_tab4:
            st.warning("This action will permanently delete the selected task.")

            confirm_delete = st.checkbox(
                "I understand that this task will be deleted permanently."
            )

            if st.button("Delete Task"):
                if not confirm_delete:
                    st.warning("Please confirm before deleting.")
                else:
                    response = delete_task(selected_task_id)

                    if response is not None and response.status_code in [200, 204]:
                        st.success("Task deleted successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to delete task.")


# ------------------------------------------------------------
# Search Tasks Section
# ------------------------------------------------------------

st.subheader("Search Tasks")

keyword = st.text_input("Search by task title")

if st.button("Search"):
    clean_keyword = safe_text(keyword)

    if not clean_keyword:
        st.warning("Please enter a search keyword.")
    else:
        search_results = search_tasks(clean_keyword)

        if search_results:
            search_df = pd.DataFrame(search_results)
            st.dataframe(search_df, use_container_width=True)
        else:
            st.info("No matching tasks found.")


# ------------------------------------------------------------
# Overdue Tasks Section
# ------------------------------------------------------------

st.subheader("Overdue Tasks")

overdue_tasks = get_overdue_tasks()

if overdue_tasks:
    overdue_df = pd.DataFrame(overdue_tasks)

    st.warning("These tasks are overdue and still pending.")
    st.dataframe(overdue_df, use_container_width=True)

else:
    st.success("No overdue tasks.")


# ------------------------------------------------------------
# Manual Refresh Button
# ------------------------------------------------------------

st.subheader("Refresh Dashboard")

if st.button("Refresh"):
    st.rerun()