import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from utils.api_client import api_client

# Page configuration
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }
    .task-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .priority-high { border-left-color: #e74c3c; }
    .priority-medium { border-left-color: #f39c12; }
    .priority-low { border-left-color: #27ae60; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.refresh_counter = 0

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/task.png", width=80)
    st.title("📋 Task Manager")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["📌 All Tasks", "➕ New Task", "📊 Dashboard", "⚠️ Overdue", "💬 Comments"],
        index=0
    )
    
    st.divider()
    
    # Filters (only on All Tasks page)
    if page == "📌 All Tasks":
        st.subheader("🔍 Filters")
        status_filter = st.multiselect(
            "Status",
            ["pending", "in_progress", "completed", "cancelled"],
            default=["pending", "in_progress"]
        )
        priority_filter = st.multiselect(
            "Priority",
            ["low", "medium", "high", "urgent"],
            default=["low", "medium", "high", "urgent"]
        )
        search_term = st.text_input("🔎 Search", placeholder="Search by title...")
    
    st.divider()
    
    # API Status
    if api_client.health_check():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Disconnected")

# Main content
if page == "📌 All Tasks":
    st.title("📌 Task List")
    
    # Get tasks with filters
    params = {}
    if status_filter:
        params['status'] = ','.join(status_filter)
    if priority_filter:
        params['priority'] = ','.join(priority_filter)
    if search_term:
        params['search'] = search_term
    
    tasks = api_client.get_tasks(**params)
    
    if tasks:
        for task in tasks:
            priority_class = f"priority-{task['priority']}"
            status_icon = {
                "pending": "🟡", "in_progress": "🔵", 
                "completed": "✅", "cancelled": "❌"
            }.get(task['status'], "⚪")
            
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="task-card {priority_class}">
                        <h4>{status_icon} {task['title']}</h4>
                        <small>Due: {datetime.fromisoformat(task['due_date']).strftime('%d/%m/%Y %H:%M')}</small><br>
                        <small>Priority: {task['priority']} | Status: {task['status']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if task['description']:
                        with st.expander("📝 Description"):
                            st.write(task['description'])
                
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        ["pending", "in_progress", "completed", "cancelled"],
                        index=["pending", "in_progress", "completed", "cancelled"].index(task['status']),
                        key=f"status_{task['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != task['status']:
                        if api_client.update_task(task['id'], {"status": new_status}):
                            st.rerun()
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                        if api_client.delete_task(task['id']):
                            st.rerun()
                
                st.divider()
    else:
        st.info("No tasks found. Create your first task!")

elif page == "➕ New Task":
    st.title("➕ Create New Task")
    
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title *", placeholder="Enter task title")
            description = st.text_area("Description", placeholder="Detailed description...")
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high", "urgent"],
                format_func=lambda x: {
                    "low": "🟢 Low", "medium": "🟠 Medium", 
                    "high": "🔴 High", "urgent": "⚡ Urgent"
                }[x]
            )
        
        with col2:
            due_date = st.date_input("Due Date", min_value=datetime.now().date())
            due_time = st.time_input("Due Time", datetime.now().time())
            assigned_to = st.text_input("Assigned To", placeholder="Person name")
            assigned_email = st.text_input("Email", placeholder="person@example.com")
            estimated_hours = st.number_input("Estimated Hours", min_value=0, max_value=100, value=0)
        
        submitted = st.form_submit_button("✅ Create Task", use_container_width=True)
        
        if submitted and title:
            due_datetime = datetime.combine(due_date, due_time)
            task_data = {
                "title": title,
                "description": description,
                "priority": priority,
                "due_date": due_datetime.isoformat(),
                "assigned_to": assigned_to if assigned_to else None,
                "assigned_email": assigned_email if assigned_email else None,
                "estimated_hours": estimated_hours
            }
            
            result = api_client.create_task(task_data)
            if result:
                st.success(f"✅ Task '{title}' created successfully!")
                st.balloons()
                st.rerun()

elif page == "📊 Dashboard":
    st.title("📊 Dashboard")
    
    stats = api_client.get_statistics()
    if stats:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Tasks", stats['total'])
        with col2:
            st.metric("Completed", stats['completed'], delta=f"{stats['completion_rate']:.0f}%")
        with col3:
            st.metric("In Progress", stats['in_progress'])
        with col4:
            st.metric("Overdue", stats['overdue'], delta="⚠️" if stats['overdue'] > 0 else "✅")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tasks by Priority")
            priority_data = pd.DataFrame({
                'Priority': list(stats['by_priority'].keys()),
                'Count': list(stats['by_priority'].values())
            })
            fig = px.pie(priority_data, values='Count', names='Priority', 
                        color='Priority', color_discrete_map={
                            'low': '#27ae60', 'medium': '#f39c12', 
                            'high': '#e67e22', 'urgent': '#e74c3c'
                        })
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Tasks by Status")
            status_data = pd.DataFrame({
                'Status': list(stats['by_status'].keys()),
                'Count': list(stats['by_status'].values())
            })
            fig = px.bar(status_data, x='Status', y='Count', color='Status')
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent tasks
        st.subheader("Recent Tasks")
        tasks = api_client.get_tasks(limit=10)
        if tasks:
            df = pd.DataFrame(tasks)
            df['due_date'] = pd.to_datetime(df['due_date'])
            df = df[['title', 'status', 'priority', 'due_date']]
            df.columns = ['Title', 'Status', 'Priority', 'Due Date']
            st.dataframe(df, use_container_width=True)

elif page == "⚠️ Overdue":
    st.title("⚠️ Overdue Tasks")
    
    overdue_tasks = api_client.get_overdue_tasks()
    
    if overdue_tasks:
        for task in overdue_tasks:
            due_date = datetime.fromisoformat(task['due_date'])
            days_overdue = (datetime.now() - due_date).days
            
            with st.expander(f"🚨 {task['title']} - {days_overdue} days overdue", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {task['description'] or 'No description'}")
                    st.write(f"**Due Date:** {due_date.strftime('%d/%m/%Y %H:%M')}")
                with col2:
                    st.write(f"**Assigned to:** {task['assigned_to'] or 'Unassigned'}")
                    st.write(f"**Email:** {task['assigned_email'] or 'Not provided'}")
                
                if st.button("✅ Mark as Completed", key=f"complete_{task['id']}"):
                    if api_client.update_task(task['id'], {"status": "completed"}):
                        st.rerun()
    else:
        st.success("🎉 No overdue tasks! Great job!")

elif page == "💬 Comments":
    st.title("💬 Task Comments")
    
    # Select task first
    tasks = api_client.get_tasks()
    if tasks:
        task_options = {f"{t['title']} (ID: {t['id']})": t['id'] for t in tasks}
        selected_task = st.selectbox("Select Task", list(task_options.keys()))
        task_id = task_options[selected_task]
        
        # Display existing comments
        comments = api_client.get_comments(task_id)
        if comments:
            st.subheader("📝 Comments")
            for comment in comments:
                with st.container():
                    st.write(f"**{comment['created_by'] or 'Anonymous'}** - {datetime.fromisoformat(comment['created_at']).strftime('%d/%m/%Y %H:%M')}")
                    st.write(comment['comment'])
                    st.divider()
        else:
            st.info("No comments yet")
        
        # Add new comment
        st.subheader("➕ Add Comment")
        with st.form("comment_form"):
            comment_text = st.text_area("Your comment")
            commenter = st.text_input("Your name (optional)")
            submitted = st.form_submit_button("Post Comment")
            
            if submitted and comment_text:
                if api_client.add_comment(task_id, comment_text, commenter):
                    st.success("Comment added!")
                    st.rerun()
    else:
        st.info("No tasks available. Create a task first to add comments.")