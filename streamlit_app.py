# Import Streamlit for frontend dashboard.
import streamlit as st

# Import requests for calling FastAPI backend.
import requests

# Import pandas for table and analytics processing.
import pandas as pd

# Import Plotly for interactive charts.
import plotly.express as px
import plotly.graph_objects as go

# Import date for due date and aging logic.
from datetime import date


# Render backend API URL.
# Use this when deploying Streamlit.
API_URL = "https://taskflow-api-st4d.onrender.com"

# For local testing only, use:
# API_URL = "http://127.0.0.1:8000"


# Configure Streamlit page.
st.set_page_config(
    page_title="TaskFlow Dashboard",
    layout="wide"
)


# Custom warm color styling.
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFF8F0;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #7C2D12;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #8A4B2A;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        color: #9A3412;
        margin-top: 30px;
        margin-bottom: 12px;
    }

    div[data-testid="metric-container"] {
        background-color: #FFE8D6;
        border: 1px solid #FDBA74;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0px 2px 8px rgba(124, 45, 18, 0.12);
    }

    section[data-testid="stSidebar"] {
        background-color: #FFEDD5;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Warm color palette for charts.
WARM_COLORS = [
    "#7C2D12",
    "#9A3412",
    "#C2410C",
    "#EA580C",
    "#F97316",
    "#FDBA74",
    "#FED7AA"
]


# Clean text input.
def safe_text(value):
    return (value or "").strip()


# Check if backend is running.
def check_backend():
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


# Get tasks from backend.
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


# Get dashboard statistics.
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


# Get overdue tasks.
def get_overdue_tasks():
    try:
        response = requests.get(f"{API_URL}/tasks/overdue", timeout=10)

        if response.status_code == 200:
            return response.json()

        return []

    except Exception:
        return []


# Create task.
def create_task(payload):
    try:
        return requests.post(
            f"{API_URL}/tasks",
            json=payload,
            timeout=10
        )
    except Exception:
        return None


# Update task.
def update_task(task_id, payload):
    try:
        return requests.put(
            f"{API_URL}/tasks/{task_id}",
            json=payload,
            timeout=10
        )
    except Exception:
        return None


# Delete task.
def delete_task(task_id):
    try:
        return requests.delete(
            f"{API_URL}/tasks/{task_id}",
            timeout=10
        )
    except Exception:
        return None


# Search tasks.
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


# Prepare analytics DataFrame.
def prepare_analytics_dataframe(tasks):
    analytics_df = pd.DataFrame(tasks)

    if analytics_df.empty:
        return analytics_df

    analytics_df["due_date"] = pd.to_datetime(
        analytics_df["due_date"],
        errors="coerce"
    )

    analytics_df["created_at"] = pd.to_datetime(
        analytics_df["created_at"],
        errors="coerce"
    )

    analytics_df["status"] = analytics_df["completed"].replace(
        {
            True: "Completed",
            False: "Pending"
        }
    )

    today = pd.to_datetime(date.today())
    due_soon_limit = today + pd.Timedelta(days=2)

    analytics_df["is_overdue"] = (
        (analytics_df["due_date"] < today) &
        (analytics_df["completed"] == False)
    )

    analytics_df["is_due_soon"] = (
        (analytics_df["due_date"] >= today) &
        (analytics_df["due_date"] <= due_soon_limit) &
        (analytics_df["completed"] == False)
    )

    analytics_df["task_age_days"] = (
        today - analytics_df["created_at"].dt.normalize()
    ).dt.days

    analytics_df["is_aging_pending"] = (
        (analytics_df["completed"] == False) &
        (analytics_df["task_age_days"] >= 3)
    )

    analytics_df["is_priority_risk"] = (
        (analytics_df["priority"] == "High") &
        (analytics_df["is_overdue"] == True)
    )

    return analytics_df


# Calculate productivity score.
def calculate_productivity_score(
    completion_rate,
    overdue_count,
    high_priority_pending_count
):
    score = completion_rate
    score = score - (overdue_count * 8)
    score = score - (high_priority_pending_count * 5)
    score = max(0, min(100, round(score, 1)))

    return score


# Main title.
st.markdown(
    '<div class="main-title">TaskFlow Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">A cloud-based task manager using FastAPI, PostgreSQL, SQLAlchemy, and Streamlit.</div>',
    unsafe_allow_html=True
)


# Backend health check.
if check_backend():
    st.success("Backend is running successfully.")
else:
    st.error("Backend is not reachable. Open the Render backend once and refresh this app.")
    st.stop()


# Sidebar task creation form.
st.sidebar.header("Create New Task")

title = st.sidebar.text_input("Task Title")
description = st.sidebar.text_area("Description")

priority_options = ["High", "Medium", "Low"]
category_options = ["Work", "College", "Personal", "Other"]

priority = st.sidebar.selectbox("Priority", priority_options)
category = st.sidebar.selectbox("Category", category_options)

due_date = st.sidebar.date_input(
    "Due Date",
    min_value=date.today()
)


# Create task action.
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
            st.sidebar.error(
                f"Failed to create task. Status code: {response.status_code}"
            )

            try:
                st.sidebar.write(response.json())
            except Exception:
                st.sidebar.write(response.text)


# Task statistics.
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


# Filters.
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


# Build filter parameters.
params = {}

if selected_priority != "All":
    params["priority"] = selected_priority

if selected_category != "All":
    params["category"] = selected_category

if sort_by != "None":
    params["sort_by"] = sort_by


# Fetch tasks.
tasks = get_tasks(params=params)


# All tasks table.
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


# Dashboard insights.
if tasks:
    st.markdown(
        '<div class="section-title">Dashboard Insights</div>',
        unsafe_allow_html=True
    )

    analytics_df = prepare_analytics_dataframe(tasks)

    total_count = len(analytics_df)
    completed_count = int((analytics_df["completed"] == True).sum())
    pending_count = int((analytics_df["completed"] == False).sum())
    overdue_count = int(analytics_df["is_overdue"].sum())
    due_soon_count = int(analytics_df["is_due_soon"].sum())
    priority_risk_count = int(analytics_df["is_priority_risk"].sum())
    aging_pending_count = int(analytics_df["is_aging_pending"].sum())

    if total_count > 0:
        completion_rate = round((completed_count / total_count) * 100, 1)
    else:
        completion_rate = 0

    high_priority_pending_count = len(
        analytics_df[
            (analytics_df["priority"] == "High") &
            (analytics_df["completed"] == False)
        ]
    )

    productivity_score = calculate_productivity_score(
        completion_rate,
        overdue_count,
        high_priority_pending_count
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    metric_col1.metric("Completion Rate", f"{completion_rate}%")
    metric_col2.metric("Due Soon", due_soon_count)
    metric_col3.metric("Priority Risk", priority_risk_count)
    metric_col4.metric("Productivity Score", f"{productivity_score}/100")

    metric_col5, metric_col6, metric_col7, metric_col8 = st.columns(4)

    metric_col5.metric("Pending Tasks", pending_count)
    metric_col6.metric("Overdue Tasks", overdue_count)
    metric_col7.metric("Aging Pending Tasks", aging_pending_count)
    metric_col8.metric("High Priority Pending", high_priority_pending_count)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        status_counts = analytics_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_status = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.45,
            color_discrete_sequence=WARM_COLORS,
            title="Completed vs Pending Tasks"
        )

        fig_status.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>Status:</b> %{label}<br><b>Tasks:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>"
        )

        st.plotly_chart(fig_status, use_container_width=True)

    with chart_col2:
        fig_score = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=productivity_score,
                title={"text": "Productivity Score"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#C2410C"},
                    "steps": [
                        {"range": [0, 40], "color": "#FEE2E2"},
                        {"range": [40, 70], "color": "#FED7AA"},
                        {"range": [70, 100], "color": "#BBF7D0"}
                    ],
                    "threshold": {
                        "line": {"color": "#7C2D12", "width": 4},
                        "thickness": 0.75,
                        "value": productivity_score
                    }
                }
            )
        )

        fig_score.update_layout(height=380)

        st.plotly_chart(fig_score, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        pending_df = analytics_df[analytics_df["completed"] == False]

        if not pending_df.empty:
            category_pending = pending_df["category"].value_counts().reset_index()
            category_pending.columns = ["Category", "Pending Tasks"]

            fig_workload = px.bar(
                category_pending,
                x="Category",
                y="Pending Tasks",
                color="Category",
                text="Pending Tasks",
                color_discrete_sequence=WARM_COLORS,
                title="Pending Workload by Category"
            )

            fig_workload.update_traces(
                hovertemplate="<b>Category:</b> %{x}<br><b>Pending Tasks:</b> %{y}<extra></extra>"
            )

            fig_workload.update_layout(showlegend=False)

            st.plotly_chart(fig_workload, use_container_width=True)

        else:
            st.success("No pending workload by category.")

    with chart_col4:
        analytics_df["risk_label"] = analytics_df["is_priority_risk"].replace(
            {
                True: "High Priority and Overdue",
                False: "Other Tasks"
            }
        )

        risk_counts = analytics_df["risk_label"].value_counts().reset_index()
        risk_counts.columns = ["Risk Type", "Count"]

        fig_risk = px.pie(
            risk_counts,
            names="Risk Type",
            values="Count",
            hole=0.45,
            color_discrete_sequence=["#DC2626", "#FDBA74"],
            title="High-Priority Overdue Risk"
        )

        fig_risk.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>Risk Type:</b> %{label}<br><b>Tasks:</b> %{value}<br><b>Percentage:</b> %{percent}<extra></extra>"
        )

        st.plotly_chart(fig_risk, use_container_width=True)

    chart_col5, chart_col6 = st.columns(2)

    with chart_col5:
        due_soon_df = analytics_df[analytics_df["is_due_soon"] == True]

        if not due_soon_df.empty:
            due_soon_display = due_soon_df[
                ["id", "title", "priority", "category", "due_date"]
            ].copy()

            due_soon_display["due_date"] = due_soon_display["due_date"].dt.date

            st.warning("These tasks are due today or within the next 2 days.")
            st.dataframe(due_soon_display, use_container_width=True)

        else:
            st.success("No tasks are due in the next 2 days.")

    with chart_col6:
        priority_counts = analytics_df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Priority", "Count"]

        fig_priority = px.bar(
            priority_counts,
            x="Priority",
            y="Count",
            color="Priority",
            text="Count",
            color_discrete_sequence=WARM_COLORS,
            title="Priority Distribution"
        )

        fig_priority.update_traces(
            hovertemplate="<b>Priority:</b> %{x}<br><b>Tasks:</b> %{y}<extra></extra>"
        )

        fig_priority.update_layout(showlegend=False)

        st.plotly_chart(fig_priority, use_container_width=True)

    chart_col7, chart_col8 = st.columns(2)

    with chart_col7:
        created_df = analytics_df.dropna(subset=["created_at"])

        if not created_df.empty:
            created_counts = created_df.groupby(
                created_df["created_at"].dt.date
            ).size().reset_index(name="Tasks Created")

            created_counts.columns = ["Created Date", "Tasks Created"]

            fig_created = px.area(
                created_counts,
                x="Created Date",
                y="Tasks Created",
                title="Tasks Created Per Day",
                color_discrete_sequence=["#C2410C"]
            )

            fig_created.update_traces(
                hovertemplate="<b>Created Date:</b> %{x}<br><b>Tasks Created:</b> %{y}<extra></extra>"
            )

            st.plotly_chart(fig_created, use_container_width=True)

        else:
            st.info("No task creation data available.")

    with chart_col8:
        aging_df = analytics_df[analytics_df["is_aging_pending"] == True]

        if not aging_df.empty:
            aging_display = aging_df[
                ["id", "title", "priority", "category", "created_at", "task_age_days"]
            ].copy()

            aging_display["created_at"] = aging_display["created_at"].dt.date

            aging_display = aging_display.sort_values(
                by="task_age_days",
                ascending=False
            )

            fig_aging = px.bar(
                aging_display,
                x="task_age_days",
                y="title",
                orientation="h",
                color="priority",
                color_discrete_sequence=WARM_COLORS,
                title="Oldest Pending Tasks",
                custom_data=["id", "category", "created_at"]
            )

            fig_aging.update_traces(
                hovertemplate=(
                    "<b>Task:</b> %{y}<br>"
                    "<b>Age:</b> %{x} days<br>"
                    "<b>Task ID:</b> %{customdata[0]}<br>"
                    "<b>Category:</b> %{customdata[1]}<br>"
                    "<b>Created At:</b> %{customdata[2]}<extra></extra>"
                )
            )

            st.plotly_chart(fig_aging, use_container_width=True)

        else:
            st.success("No aging pending tasks found.")

    st.markdown(
        '<div class="section-title">Actionable Insights</div>',
        unsafe_allow_html=True
    )

    if completion_rate >= 80:
        st.success("Strong progress. More than 80% of your tasks are completed.")
    elif completion_rate >= 50:
        st.info("Moderate progress. You have completed at least half of your tasks.")
    else:
        st.warning("Completion rate is below 50%. Focus on completing pending tasks.")

    if due_soon_count > 0:
        st.warning(f"{due_soon_count} task(s) are due today or within the next 2 days.")
    else:
        st.success("No urgent due-soon tasks found.")

    if priority_risk_count > 0:
        st.error(f"{priority_risk_count} high-priority task(s) are overdue.")
    else:
        st.success("No high-priority overdue tasks found.")

    if aging_pending_count > 0:
        st.warning(f"{aging_pending_count} pending task(s) have been open for 3 or more days.")
    else:
        st.success("No old pending tasks found.")

    if productivity_score >= 80:
        st.success("Productivity score is strong.")
    elif productivity_score >= 50:
        st.info("Productivity score is moderate.")
    else:
        st.warning("Productivity score is low. Handle overdue and high-priority tasks first.")


# Task actions.
if tasks:
    st.markdown(
        '<div class="section-title">Task Actions</div>',
        unsafe_allow_html=True
    )

    task_ids = [task["id"] for task in tasks]

    selected_task_id = st.selectbox("Select Task ID", task_ids)

    selected_task = None

    for task in tasks:
        if task["id"] == selected_task_id:
            selected_task = task
            break

    if selected_task is not None:
        edit_tab, complete_tab, reopen_tab, delete_tab = st.tabs(
            ["Edit Task", "Mark Completed", "Reopen Task", "Delete Task"]
        )

        with edit_tab:
            edited_title = st.text_input(
                "Edit Title",
                value=selected_task.get("title", "")
            )

            edited_description = st.text_area(
                "Edit Description",
                value=selected_task.get("description") or ""
            )

            current_priority = selected_task.get("priority", "Medium")
            priority_index = priority_options.index(current_priority) if current_priority in priority_options else 1

            edited_priority = st.selectbox(
                "Edit Priority",
                priority_options,
                index=priority_index
            )

            current_category = selected_task.get("category", "Other")
            category_index = category_options.index(current_category) if current_category in category_options else 3

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

                    response = update_task(selected_task_id, update_payload)

                    if response is not None and response.status_code == 200:
                        st.success("Task updated successfully.")
                        st.rerun()
                    else:
                        st.error("Failed to update task.")

        with complete_tab:
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


# Search section.
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


# Overdue tasks section.
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


# Refresh section.
st.markdown(
    '<div class="section-title">Refresh Dashboard</div>',
    unsafe_allow_html=True
)

if st.button("Refresh"):
    st.rerun()
