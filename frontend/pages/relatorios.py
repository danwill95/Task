import streamlit as st
from utils.api_client import api_client
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Reports", layout="wide")

st.title("📈 Reports")

# Date range selector
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", datetime.now())

# Generate report
tasks = api_client.get_tasks()
if tasks:
    df = pd.DataFrame(tasks)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['due_date'] = pd.to_datetime(df['due_date'])
    
    # Filter by date range
    mask = (df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)
    filtered_df = df[mask]
    
    st.subheader(f"Report Period: {start_date} to {end_date}")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Export option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV Report",
        data=csv,
        file_name=f"task_report_{start_date}_{end_date}.csv",
        mime="text/csv"
    )