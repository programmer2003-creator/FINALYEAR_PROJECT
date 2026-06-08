# streamlit_app.py
"""
Streamlit Application for Petroleum Price Forecasting
Connects to an existing PostgreSQL DB (does NOT create or alter tables).
Reflection and SQLAlchemy 2.0-compatible classical mapping are used.
"""

import streamlit as st
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, registry
from datetime import datetime
import re
import bcrypt
import os

# ---------- DB config (use your provided values) ----------
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'forecast_DB',
    'user': 'postgres',
    'password': 'wense2703'
}

DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# ---------- Engine and session ----------
try:
    engine = create_engine(DB_URL, echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    DB_OK = True
    DB_ERROR = ""
except Exception as e:
    engine = None
    SessionLocal = None
    DB_OK = False
    DB_ERROR = str(e)

# ---------- Reflect existing tables and map them (SQLAlchemy 2.0) ----------
User = None
Log = None
users_table = None
logs_table = None
password_column_name = None
created_at_column_name = None

if DB_OK:
    try:
        metadata = MetaData()
        # reflect only the tables you need; adjust names if your tables differ
        metadata.reflect(bind=engine, only=['users', 'logs'])
        users_table = metadata.tables.get('users')
        logs_table = metadata.tables.get('logs')

        if users_table is None:
            raise RuntimeError("Table 'users' not found in database")
        if logs_table is None:
            raise RuntimeError("Table 'logs' not found in database")

        # Inspect columns to find password and created_at column names (safe assignment)
        user_cols = [c.name for c in users_table.columns]
        # prefer 'password_hash', then 'password', then any column containing 'pass'
        if 'password_hash' in user_cols:
            password_column_name = 'password_hash'
        elif 'password' in user_cols:
            password_column_name = 'password'
        else:
            found = next((c for c in user_cols if 'pass' in c.lower()), None)
            password_column_name = found

        # detect created_at-like column
        if 'created_at' in user_cols:
            created_at_column_name = 'created_at'
        elif 'created' in user_cols:
            created_at_column_name = 'created'
        else:
            created_at_column_name = None

        # Use registry for classical mapping (SQLAlchemy 2.0)
        mapper_registry = registry()

        class User: pass
        class Log: pass

        mapper_registry.map_imperatively(User, users_table)
        mapper_registry.map_imperatively(Log, logs_table)

    except Exception as e:
        DB_OK = False
        DB_ERROR = f"Reflection/mapping failed: {e}"

# ---------- Validation helpers ----------
def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    return True, "Password is strong"

# ---------- Streamlit helpers ----------
def get_client_info():
    # Streamlit does not expose client IP reliably; placeholder used.
    return {"ip": "127.0.0.1", "user_agent": st.session_state.get("_user_agent", "streamlit")}

def add_log(db, **kwargs):
    try:
        log = Log(**kwargs)
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

def set_user_password_field(user_obj, hashed_password):
    """
    Assign hashed password to the correct attribute on the reflected User object.
    Uses detected password_column_name; falls back to trying common names.
    """
    global password_column_name
    if password_column_name:
        setattr(user_obj, password_column_name, hashed_password)
        return
    # fallback attempts
    for candidate in ('password_hash', 'password', 'passwd'):
        if hasattr(user_obj, candidate):
            setattr(user_obj, candidate, hashed_password)
            return
    # last resort: set attribute 'password_hash'
    setattr(user_obj, 'password_hash', hashed_password)

def get_user_password_value(user_obj):
    """
    Return the stored password hash from the user object using detected column name.
    """
    global password_column_name
    if password_column_name and hasattr(user_obj, password_column_name):
        return getattr(user_obj, password_column_name)
    for candidate in ('password_hash', 'password', 'passwd'):
        if hasattr(user_obj, candidate):
            return getattr(user_obj, candidate)
    return None

# ---------- Session state ----------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# ---------- Sidebar ----------
def sidebar_nav():
    st.sidebar.title("Navigation")
    st.sidebar.markdown("**Pages**")
    pages = [
        ("Home", "home"),
        ("User Dashboard", "user_dashboard"),
        ("Visualization App", "visualization_app"),
        ("Forecast App", "forecast_app"),
        ("Register", "register"),
        ("Login", "login"),
    ]
    for label, key in pages:
        if st.sidebar.button(label, key=f"nav_{key}"):
            st.session_state.page = key

    st.sidebar.markdown("---")
    if DB_OK:
        st.sidebar.success("DB: connected")
    
    else:
        st.sidebar.error("DB: connection failed")
        st.sidebar.caption(DB_ERROR)
    st.sidebar.markdown("---")
    if st.session_state.user_id:
        st.sidebar.write(f"**Signed in as**\n\n{st.session_state.username}")
        if st.sidebar.button("Logout", key="sidebar_logout"):
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
            st.session_state.page = "home"
            st.experimental_rerun()

# ---------- Pages ----------
def home_page():
    st.title("Petroleum Price Forecasting System")
    st.markdown("Welcome. Use the sidebar to navigate between pages.")
    st.markdown("---")
    st.markdown("**About**")
    st.write("This app forecasts petroleum prices using Prophet and stores user data in PostgreSQL.")
    st.markdown("---")
    st.caption("© 2026 | Petroleum Price Forecasting System")

def register_page():
    st.header("Register")
    if not DB_OK:
        st.error("Database connection is not available. Registration is disabled.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
        return

    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Create account")

        if submitted:
            errors = []
            if not username or len(username) < 3:
                errors.append("Username must be at least 3 characters")
            if not email or not is_valid_email(email):
                errors.append("Valid email is required")
            is_strong, msg = is_strong_password(password)
            if not is_strong:
                errors.append(msg)
            if password != password_confirm:
                errors.append("Passwords do not match")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Normalize email
                email_norm = email.strip().lower()

                db = SessionLocal()
                try:
                    # Check existing user/email
                    existing_user = db.query(User).filter_by(username=username).first()
                    existing_email = db.query(User).filter_by(email=email_norm).first()
                    if existing_user:
                        st.error("Username already exists")
                    elif existing_email:
                        st.error("Email already registered")
                    else:
                        # Hash password with bcrypt (create bytes then decode to str)
                        hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                        hashed = hashed_bytes.decode("utf-8")  # e.g. "$2b$12$..."

                        new_user = User()
                        # assign username
                        if hasattr(new_user, 'username'):
                            setattr(new_user, 'username', username)
                        else:
                            for cand in ('user_name', 'user', 'uname'):
                                if hasattr(new_user, cand):
                                    setattr(new_user, cand, username)
                                    break

                        # assign email
                        if hasattr(new_user, 'email'):
                            setattr(new_user, 'email', email_norm)
                        else:
                            for cand in ('e_mail',):
                                if hasattr(new_user, cand):
                                    setattr(new_user, cand, email_norm)
                                    break

                        # set password in the correct column
                        set_user_password_field(new_user, hashed)

                        # set created_at if column exists
                        if created_at_column_name and hasattr(new_user, created_at_column_name):
                            setattr(new_user, created_at_column_name, datetime.utcnow())

                        db.add(new_user)
                        db.commit()
                        db.refresh(new_user)

                        # Optional integrity check
                        stored = get_user_password_value(new_user) or ""
                        if not (isinstance(stored, str) and stored.startswith("$2") and 50 <= len(stored) <= 255):
                            db.rollback()
                            st.error("Registration failed: stored password hash has unexpected format")
                        else:
                            client = get_client_info()
                            add_log(db,
                                    user_type="user",
                                    user_id=getattr(new_user, 'id', None),
                                    username=username,
                                    email=email_norm,
                                    login_status="registered",
                                    ip_address=client["ip"],
                                    user_agent=client["user_agent"]
                                    )
                            st.success(f"Registration successful! Welcome {username}. You can now log in.")
                            st.session_state.page = "login"
                except Exception as e:
                    db.rollback()
                    st.error(f"Registration failed: {e}")
                finally:
                    db.close()

    if st.button("Back to Home"):
        st.session_state.page = "home"


def login_page():
    st.header("Login")
    if not DB_OK:
        st.error("Database connection is not available. Login is disabled.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
        return

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(username=username).first()
                client = get_client_info()
                if user:
                    stored_hash = get_user_password_value(user)
                    if stored_hash and bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                        st.success(f"Welcome back, {getattr(user, 'username', username)}!")
                        st.session_state.user_id = getattr(user, 'id', None)
                        st.session_state.username = getattr(user, 'username', username)
                        st.session_state.page = "user_dashboard"

                        add_log(db,
                                user_type="user",
                                user_id=getattr(user, 'id', None),
                                username=getattr(user, 'username', username),
                                email=getattr(user, 'email', None),
                                login_status="success",
                                ip_address=client["ip"],
                                user_agent=client["user_agent"]
                                )
                    else:
                        add_log(db,
                                user_type="user",
                                username=username,
                                login_status="failed",
                                ip_address=client["ip"],
                                user_agent=client["user_agent"],
                                failure_reason="Invalid credentials"
                                )
                        st.error("Invalid username or password")
                else:
                    add_log(db,
                            user_type="user",
                            username=username,
                            login_status="failed",
                            ip_address=client["ip"],
                            user_agent=client["user_agent"],
                            failure_reason="User not found"
                            )
                    st.error("Invalid username or password")
            except Exception as e:
                st.error(f"Login error: {e}")
            finally:
                db.close()

    if st.button("Back to Home"):
        st.session_state.page = "home"

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

def visualization_app_page():
    st.header("Visualization App")
    st.write("Placeholder for visualization_app.py. Add charts and interactive controls here.")

def forecast_app_page():
    st.header("Forecast App")
    st.write("Placeholder for forecast_app.py. Add forecasting UI and model controls here.")

# ---------- Router ----------
def router():
    sidebar_nav()
    page = st.session_state.page
    if page == "home":
        home_page()
    elif page == "register":
        register_page()
    elif page == "login":
        login_page()
    elif page == "user_dashboard":
        user_dashboard_page()
    elif page == "visualization_app":
        visualization_app_page()
    elif page == "forecast_app":
        forecast_app_page()
    else:
        st.session_state.page = "home"
        home_page()

# Run the app
if __name__ == "__main__":
    st.set_page_config(page_title="Petroleum Price Forecasting", layout="centered")
    if not DB_OK:
        st.warning("Database connection failed. Some features are disabled.")
        st.caption(DB_ERROR)
    router()
