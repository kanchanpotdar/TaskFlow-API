import streamlit as st
import requests
import pandas as pd
from datetime import date

# Backend API
API_URL = "https://taskflow-api-st4d.onrender.com"

st.set_page_config(page_title="TaskFlow Dashboard", layout="wide")

# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------
def safe_text(value):
    return (value or "").strip()

# ------------------------------------------------------------
# API Calls
# ------------------------------------------------------------
def get_tasks(params=None):
    try:
        r = requests.get(f"{API_URL}/tasks", params=params, timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_stats():
    try:
        r = requests.get(f"{API_URL}/stats", timeout=5)
        return r.json()
    except:
        return {"total_tasks": 0, "completed": 0, "pending": 0, "overdue": 0}

def create_task(payload):
    try:
        return requests.post(f"{API_URL}/tasks", json=payload)
    except:
        return None

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.title("TaskFlow Dashboard")

# ------------------------------------------------------------
# Sidebar (CREATE TASK)
# ------------------------------------------------------------
st.sidebar.header("Create New Task")

title = st.sidebar.text_input("Task Title")
description = st.sidebar.text_area("Description")

priority = st.sidebar.selectbox("Priority", ["High", "Medium", "Low"])

category = st.sidebar.selectbox(
    "Category",
    ["Work", "College", "Personal", "Other"]
)

due_date = st.sidebar.date_input("Due Date", min_value=date.today())

if st.sidebar.button("Create Task"):
    if not safe_text(title):
        st.warning("Title required")
    else:
        payload = {
            "title": safe_text(title),
            "description": safe_text(description),
            "priority": priority,
            "category": category,
            "due_date": str(due_date)
        }

        res = create_task(payload)
        if res and res.status_code in [200, 201]:
            st.success("Task created")
            st.rerun()

# ------------------------------------------------------------
# Stats
# ------------------------------------------------------------
stats = get_stats()
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", stats["total_tasks"])
col2.metric("Completed", stats["completed"])
col3.metric("Pending", stats["pending"])
col4.metric("Overdue", stats["overdue"])

# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------
st.subheader("Filters")

c1, c2, c3 = st.columns(3)

with c1:
    selected_priority = st.selectbox("Priority", ["All", "High", "Medium", "Low"])

with c2:
    selected_category = st.selectbox(
        "Category",
        ["All", "Work", "College", "Personal", "Other"]
    )

with c3:
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

# ------------------------------------------------------------
# FETCH TASKS
# ------------------------------------------------------------
tasks = get_tasks(params)

st.subheader("All Tasks")

if tasks:
    df = pd.DataFrame(tasks)

    df = df[[
        "id", "title", "priority", "category",
        "due_date", "completed"
    ]]

    st.dataframe(df, use_container_width=True)

# ------------------------------------------------------------
# ANALYTICS
# ------------------------------------------------------------
if tasks:
    st.subheader("Analytics")

    colA, colB = st.columns(2)

    df = pd.DataFrame(tasks)

    with colA:
        st.write("Tasks by Category")
        st.bar_chart(df["category"].value_counts())

    with colB:
        st.write("Completion Status")
        st.bar_chart(df["completed"].value_counts())
