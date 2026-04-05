import streamlit as st
from utils.api_client import api_client
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 Analytics Dashboard")

stats = api_client.get_statistics()
if stats:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Tasks", stats['total'])
    with col2:
        st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
    with col3:
        st.metric("Active Tasks", stats['total'] - stats['completed'])
    with col4:
        st.metric("Overdue", stats['overdue'])
    
    # Add more detailed analytics here