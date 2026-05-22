import streamlit as st
import requests
import pandas as pd
from datetime import date


API_URL = "https://taskflow-api-st4d.onrender.com"


st.set_page_config(
    page_title="TaskFlow Dashboard",
    layout="wide"
)


st.markdown(
    """
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #1f4e79;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        color: #555;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: #263238;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def safe_text(value):
    return (value or "").strip()


def check_backend():
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def get_tasks(params=None):
    try:
        response = requests.get(
            f"{API_URL}/tasks",
            params=params,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        st.error(f"Failed to load tasks. Status code: {response.status_code}")
        try:
            st.write(response.json())
        except Exception:
            st.write(response.text)

        return []

    except Exception as error:
        st.error("Could not connect to backend while loading tasks.")
        st.write(str(error))
        return []


def get_stats():
    default_stats = {
        "total_tasks": 0,
        "completed": 0,
        "pending": 0,
        "overdue": 0
    }

    try:
        response = requests.get(f"{API_URL}/stats", timeout=10)

        if response.status_code == 200:
            return response.json()

        return default_stats

    except Exception:
        return default_stats


def get_overdue_tasks():
    try:
        response = requests.get(f"{API_URL}/tasks/overdue", timeout=10)

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


def create_task(payload):
    try:
        return requests.post(
            f"{API_URL}/tasks",
            json=payload,
            timeout=10
        )
    except Exception:
        return None


def update_task(task_id, payload):
    try:
        return requests.put(
            f"{API_URL}/tasks/{task_id}",
            json=payload,
            timeout=10
        )
    except Exception:
        return None


def delete_task(task_id):
    try:
        return requests.delete(
            f"{API_URL}/tasks/{task_id}",
            timeout=10
        )
    except Exception:
        return None


def search_tasks(keyword):
    try:
        response = requests.get(
            f"{API_URL}/tasks/search",
            params={"keyword": keyword},
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


st.markdown(
    '<div class="main-title">TaskFlow Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">A cloud-based task manager using FastAPI, PostgreSQL, and Streamlit.</div>',
    unsafe_allow_html=True
)


if check_backend():
    st.success("Backend is running successfully.")
else:
    st.error("Backend is not reachable. Open the Render backend once and refresh this app.")
    st.stop()


st.sidebar.header("Create New Task")

title = st.sidebar.text_input("Task Title")
description = st.sidebar.text_area("Description")

priority_options = ["High", "Medium", "Low"]
category_options = ["Work", "College", "Personal", "Other"]

priority = st.sidebar.selectbox(
    "Priority",
    priority_options
)

category = st.sidebar.selectbox(
    "Category",
    category_options
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
            "category": category,
            "due_date": str(due_date)
        }

        response = create_task(payload)

        if response is None:
            st.sidebar.error("Could not connect to backend.")
        elif response.status_code in [200, 201]:
            st.sidebar.success("Task created successfully.")
            st.rerun()
        else:
            st.sidebar.error(f"Failed to create task. Status code: {response.status_code}")
            try:
                st.sidebar.write(response.json())
            except Exception:
                st.sidebar.write(response.text)


st.markdown(
    '<div class="section-title">Task Statistics</div>',
    unsafe_allow_html=True
)

stats = get_stats()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tasks", stats.get("total_tasks", 0))
col2.metric("Completed", stats.get("completed", 0))
col3.metric("Pending", stats.get("pending", 0))
col4.metric("Overdue", stats.get("overdue", 0))


st.markdown(
    '<div class="section-title">Filters</div>',
    unsafe_allow_html=True
)

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_priority = st.selectbox(
        "Filter by Priority",
        ["All", "High", "Medium", "Low"]
    )

with filter_col2:
    selected_category = st.selectbox(
        "Filter by Category",
        ["All", "Work", "College", "Personal", "Other"]
    )

with filter_col3:
    sort_by = st.selectbox(
        "Sort By",
        ["None", "due_date", "priority", "created_at"]
    )


params = {}

if selected_priority != "All":
    params["priority"] = selected_priority

if selected_category != "All":
    params["category"] = selected_category

if sort_by != "None":
    params["sort_by"] = sort_by


tasks = get_tasks(params=params)


st.markdown(
    '<div class="section-title">All Tasks</div>',
    unsafe_allow_html=True
)

if tasks:
    df = pd.DataFrame(tasks)

    display_columns = [
        "id",
        "title",
        "description",
        "priority",
        "category",
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


if tasks:
    st.markdown(
        '<div class="section-title">Dashboard Insights</div>',
        unsafe_allow_html=True
    )

    analytics_df = pd.DataFrame(tasks)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("Tasks by Category")
        if "category" in analytics_df.columns:
            st.bar_chart(analytics_df["category"].value_counts())

    with chart_col2:
        st.write("Tasks by Priority")
        if "priority" in analytics_df.columns:
            st.bar_chart(analytics_df["priority"].value_counts())

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.write("Completion Status")
        status_counts = analytics_df["completed"].replace(
            {
                True: "Completed",
                False: "Pending"
            }
        ).value_counts()
        st.bar_chart(status_counts)

    with chart_col4:
        st.write("Pending Tasks by Category")
        pending_df = analytics_df[analytics_df["completed"] == False]

        if not pending_df.empty and "category" in pending_df.columns:
            st.bar_chart(pending_df["category"].value_counts())
        else:
            st.info("No pending tasks.")


if tasks:
    st.markdown(
        '<div class="section-title">Task Actions</div>',
        unsafe_allow_html=True
    )

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
        edit_tab, complete_tab, reopen_tab, delete_tab = st.tabs(
            [
                "Edit Task",
                "Mark Completed",
                "Reopen Task",
                "Delete Task"
            ]
        )

        with edit_tab:
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

            current_category = selected_task.get("category", "Other")

            if current_category in category_options:
                category_index = category_options.index(current_category)
            else:
                category_index = 3

            edited_category = st.selectbox(
                "Edit Category",
                category_options,
                index=category_index
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
                        "category": edited_category,
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
                        if response is not None:
                            try:
                                st.write(response.json())
                            except Exception:
                                st.write(response.text)

        with complete_tab:
            st.write("Mark the selected task as completed.")

            if bool(selected_task.get("completed", False)):
                st.info("This task is already completed.")
            else:
                if st.button("Mark as Completed"):
                    response = update_task(
                        selected_task_id,
                        {"completed": True}
                    )

                    if response is not None and response.status_code == 200:
                        st.success("Task marked as completed.")
                        st.rerun()
                    else:
                        st.error("Failed to mark task as completed.")

        with reopen_tab:
            st.write("Reopen a completed task and mark it as pending.")

            if not bool(selected_task.get("completed", False)):
                st.info("This task is already pending.")
            else:
                if st.button("Reopen Task"):
                    response = update_task(
                        selected_task_id,
                        {"completed": False}
                    )

                    if response is not None and response.status_code == 200:
                        st.success("Task reopened successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to reopen task.")

        with delete_tab:
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


st.markdown(
    '<div class="section-title">Search Tasks</div>',
    unsafe_allow_html=True
)

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


st.markdown(
    '<div class="section-title">Overdue Tasks</div>',
    unsafe_allow_html=True
)

overdue_tasks = get_overdue_tasks()

if overdue_tasks:
    overdue_df = pd.DataFrame(overdue_tasks)
    st.warning("These tasks are overdue and still pending.")
    st.dataframe(overdue_df, use_container_width=True)
else:
    st.success("No overdue tasks.")


st.markdown(
    '<div class="section-title">Refresh Dashboard</div>',
    unsafe_allow_html=True
)

if st.button("Refresh"):
    st.rerun()