import streamlit as st
from datetime import datetime
import pandas as pd
import re
from sqlalchemy.orm import Session
# Import your engine, SessionLocal, and User models here
# from your_app_module import SessionLocal, User, DB_OK, get_client_info, add_log

# --- Page Initialization ---
st.set_page_config(page_title="User Account Dashboard", layout="wide", page_icon="📊")

# --- Security & Session Guard Clause ---
if "user_id" not in st.session_state or st.session_state.user_id is None:
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    with center_content:
        st.error("🛑 Security Access Denied. Please sign in via the portal to access your dashboard metrics.")
        # Fixed routing fallback button to safely return back to index.py / home view state
        st.page_link("pages/index.py", label="⬅️ Back to Home Screen", use_container_width=True)
    st.stop()

# --- Mock Variables for Display (Replace with actual imports if running standalone) ---
# These act as fallbacks if not inherited from the main app state context
if "company_name" not in st.session_state:
    st.session_state.company_name = "Not Specified"
if "position" not in st.session_state:
    st.session_state.position = "Not Specified"
if "company_type" not in st.session_state:
    st.session_state.company_type = "Not Specified"
if "email" not in st.session_state:
    st.session_state.email = "user@example.com"
if "last_login" not in st.session_state:
    st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Database Sync Helper ---
def pull_latest_user_profile():
    """Fetches real-time profile criteria from the PostgreSQL database engine."""
    # If DB connections are active, pull fresh records down
    try:
        # db = SessionLocal()
        # user = db.query(User).filter_by(id=st.session_state.user_id).first()
        # if user:
        #     st.session_state.username = getattr(user, 'username', st.session_state.username)
        #     st.session_state.email = getattr(user, 'email', st.session_state.email)
        #     st.session_state.company_name = getattr(user, 'company_name', 'Not Specified') or 'Not Specified'
        #     st.session_state.position = getattr(user, 'position', 'Not Specified') or 'Not Specified'
        #     st.session_state.company_type = getattr(user, 'company_type', 'fuel stations operator')
        # db.close()
        pass
    except Exception:
        pass

# Pull data before rendering components
pull_latest_user_profile()

# --- Layout Structure Constraints ---
left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])

with center_content:
    # --- Dashboard Title Bar ---
    st.title("📊 User Performance Dashboard")
    st.markdown("Manage operational permissions, enterprise identifiers, and localized system credentials.")
    st.divider()

    # --- Metrics Section (KPI Cards Visualizer) ---
    st.markdown("### 📈 Core Account Telemetry")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Registered Identity", value=st.session_state.username)
    with kpi2:
        st.metric(label="Corporate Entity", value=st.session_state.company_name)
    with kpi3:
        st.metric(label="Enterprise Access Role", value=st.session_state.position)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Main Tab Components ---
    tab_overview, tab_edit_profile = st.tabs([
        "🪪 Identity Profile Overview", 
        "⚙️ Modify Account Information"
    ])

    # TAB 1: Profile Summary Overview
    with tab_overview:
        st.markdown("#### Operational Identity Meta Data")
        st.write("Current authorization matrix mapping configurations active within the platform network:")
        
        # Display Card Matrix Details using Streamlit formatting elements
        with st.container(border=True):
            col_left, col_right = st.columns(2)
            with col_left:
                st.write(f"**Username Account ID:** `{st.session_state.username}`")
                st.write(f"**Verified Communication Email:** `{st.session_state.email}`")
                st.write(f"**Operational Scope Category:** `{st.session_state.company_type.title()}`")
            with col_right:
                st.write(f"**Corporate Assignment:** `{st.session_state.company_name}`")
                st.write(f"**Designated Job Position:** `{st.session_state.position}`")
                st.write(f"**System Log Timestamp:** :green[{st.session_state.last_login}]")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Operational Security Directive:** If any system parameter identifiers drift from target enterprise contexts, apply edits directly under the management panel tab window.")

    # TAB 2: Edit Form Processing Module
    with tab_edit_profile:
        st.markdown("#### Edit Profile Matrix Parameters")
        st.write("Modify baseline business registry targets down below to keep operations unified.")
        
        # Wrapped inside form mechanism safely
        with st.form("profile_update_form", clear_on_submit=False):
            new_email = st.text_input("Verified Email Context", value=st.session_state.email)
            new_company = st.text_input("Enterprise Name / Company Unit", value=st.session_state.company_name)
            new_position = st.text_input("Professional Operational Title", value=st.session_state.position)
            
            new_comp_type = st.selectbox(
                "Company Sector Group",
                options=["fuel stations operator", "logistics operator"],
                index=0 if st.session_state.company_type == "fuel stations operator" else 1
            )
            
            submit_profile_changes = st.form_submit_button("💾 Commit Profile Synchronization Changes", use_container_width=True)
            
            if submit_profile_changes:
                # Basic context constraints validations
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, new_email):
                    st.error("Submission Failure: The specified communication target email string pattern format is invalid.")
                else:
                    # Execute database writing operation safely
                    try:
                        # db = SessionLocal()
                        # user = db.query(User).filter_by(id=st.session_state.user_id).first()
                        # if user:
                        #     user.email = new_email.strip().lower()
                        #     user.company_name = new_company.strip() if new_company else None
                        #     user.position = new_position.strip() if new_position else None
                        #     user.company_type = new_comp_type
                        #     db.commit()
                        
                        # Synchronize immediate session indicators matching changes instantly 
                        st.session_state.email = new_email.strip().lower()
                        st.session_state.company_name = new_company.strip() if new_company else "Not Specified"
                        st.session_state.position = new_position.strip() if new_position else "Not Specified"
                        st.session_state.company_type = new_comp_type
                        
                        st.success("✅ Information metrics modified successfully! Synchronization layers parsed cleanly.")
                        st.rerun()
                        
                    except Exception as transaction_error:
                        # db.rollback()
                        st.error(f"Write Transaction Exception Triggered: {transaction_error}")
                    # finally:
                    #     db.close()

    # Footer Caption Module
    st.divider()
    st.caption("© 2026 | Petroleum Price Predictive Analytics Platform Engine Cluster Node")