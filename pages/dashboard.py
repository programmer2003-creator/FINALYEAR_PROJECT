
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Sidebar - User Details and Services
with st.sidebar:
    st.markdown("---")
    st.subheader(" User Details")
    
    # User information
    user_name = "Admin User"
    user_email = "admin@example.com"
    user_role = "Analyst"
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("👤")
    with col2:
        st.markdown(f"**{user_name}**")
    
    st.caption(f"📧 {user_email}")
    st.caption(f"🔖 Role: {user_role}")
    st.caption(f"📅 Last Login: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    st.markdown(
        """
        <div style='text-align: center; font-size: 0.8em; color: #666;'>
        <p>Dashboard v1.0</p>
        <p>© 2026 | Petroleum Price Forecasting System</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
def user_dashboard_page():
    if not st.session_state.user_id:
        st.warning("Please log in first")
        st.session_state.page = "login"
        return

    st.header("User Dashboard")
    st.write(f"Hello, **{st.session_state.username}**")
    st.markdown("This is the user dashboard. Replace with your real dashboard UI.")
    if st.button("Logout"):
        if DB_OK:
            db = SessionLocal()
            try:
                add_log(db,
                        user_type="user",
                        user_id=st.session_state.user_id,
                        username=st.session_state.username,
                        login_status="logout",
                        ip_address=get_client_info()["ip"],
                        user_agent=get_client_info()["user_agent"],
                        logout_time=datetime.utcnow()
                        )
            finally:
                db.close()
        st.session_state.user_id = None
        st.session_state.username = None
        st.success("You have been logged out")
        st.session_state.page = "home"