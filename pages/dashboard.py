import streamlit as st

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