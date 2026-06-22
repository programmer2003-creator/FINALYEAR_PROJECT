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

# --- MUST BE THE VERY FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Petroleum Price Forecasting", layout="wide")

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
        metadata.reflect(bind=engine, only=['users', 'logs'])
        users_table = metadata.tables.get('users')
        logs_table = metadata.tables.get('logs')

        if users_table is None:
            raise RuntimeError("Table 'users' not found in database")
        if logs_table is None:
            raise RuntimeError("Table 'logs' not found in database")

        user_cols = [c.name for c in users_table.columns]
        if 'password_hash' in user_cols:
            password_column_name = 'password_hash'
        elif 'password' in user_cols:
            password_column_name = 'password'
        else:
            found = next((c for c in user_cols if 'pass' in c.lower()), None)
            password_column_name = found

        if 'created_at' in user_cols:
            created_at_column_name = 'created_at'
        elif 'created' in user_cols:
            created_at_column_name = 'created'
        else:
            created_at_column_name = None

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
    return {"ip": "127.0.0.1", "user_agent": st.session_state.get("_user_agent", "streamlit")}

def add_log(db, **kwargs):
    try:
        log = Log(**kwargs)
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

def set_user_password_field(user_obj, hashed_password):
    global password_column_name
    if password_column_name:
        setattr(user_obj, password_column_name, hashed_password)
        return
    for candidate in ('password_hash', 'password', 'passwd'):
        if hasattr(user_obj, candidate):
            setattr(user_obj, candidate, hashed_password)
            return
    setattr(user_obj, 'password_hash', hashed_password)

def get_user_password_value(user_obj):
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

# ---------- Clean Sidebar Dynamic Monitor ----------
def render_sidebar_status():
    st.sidebar.title("System Status")
    if DB_OK:
        st.sidebar.success("DB: connected")
    else:
        st.sidebar.error("DB: connection failed")
        st.sidebar.caption(DB_ERROR)
    
    st.sidebar.markdown("---")
    if st.session_state.user_id:
        st.sidebar.write(f"**Signed in as:**\n\n{st.session_state.username}")
        if st.sidebar.button("Logout", key="sidebar_logout", use_container_width=True):
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
            st.rerun()

# ---------- Main Screen Component Routing Windows ----------
def home_page():
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    
    with center_content:
        st.title("⛽ Petroleum Price Forecasting System")
        st.markdown("Welcome to the analytical portal. Please sign in or register below to access interactive projection modules.")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔑 Login Portal", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
        with btn_col2:
            if st.button("📝 Register Account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
                
        st.divider()
        st.markdown("#### **About System Platform**")
        st.write("This engine processes localized downstream petroleum variables using predictive architectures to support retail station operations and logistical mitigation metrics.")
        st.caption("© 2026 | Petroleum Price Forecasting System")

def register_page():
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    with center_content:
        st.header("📝 Create System Account")
        if not DB_OK:
            st.error("Database connection is not available. Registration is disabled.")
            if st.button("Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            return

        with st.form("register_form"):
            st.markdown("##### **Account Credentials**")
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                password = st.text_input("Password*", type="password")
            with col2:
                email = st.text_input("Email*")
                password_confirm = st.text_input("Confirm Password*", type="password")
            
            st.markdown("---")
            st.markdown("##### **Corporate & Operational Details**")
            company_name = st.text_input("Company Name")
            position = st.text_input("Your Position / Role")
            
            company_type = st.selectbox(
                "Company Operation Type",
                options=["fuel stations operator", "logistics operator"],
                index=0
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Create Account", use_container_width=True)

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
                    email_norm = email.strip().lower()
                    db = SessionLocal()
                    try:
                        existing_user = db.query(User).filter_by(username=username).first()
                        existing_email = db.query(User).filter_by(email=email_norm).first()
                        if existing_user:
                            st.error("Username already exists")
                        elif existing_email:
                            st.error("Email already registered")
                        else:
                            hashed_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                            hashed = hashed_bytes.decode("utf-8")

                            new_user = User()
                            
                            if hasattr(new_user, 'username'):
                                setattr(new_user, 'username', username)
                            else:
                                for cand in ('user_name', 'user', 'uname'):
                                    if hasattr(new_user, cand):
                                        setattr(new_user, cand, username)
                                        break

                            if hasattr(new_user, 'email'):
                                setattr(new_user, 'email', email_norm)
                            else:
                                for cand in ('e_mail',):
                                    if hasattr(new_user, cand):
                                        setattr(new_user, cand, email_norm)
                                        break

                            set_user_password_field(new_user, hashed)

                            if hasattr(new_user, 'company_name'):
                                setattr(new_user, 'company_name', company_name.strip() if company_name else None)
                            if hasattr(new_user, 'position'):
                                setattr(new_user, 'position', position.strip() if position else None)
                            if hasattr(new_user, 'company_type'):
                                setattr(new_user, 'company_type', company_type)

                            if created_at_column_name and hasattr(new_user, created_at_column_name):
                                setattr(new_user, created_at_column_name, datetime.utcnow())

                            db.add(new_user)
                            db.commit()
                            db.refresh(new_user)

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
                                st.success(f"Registration successful! Welcome {username}.")
                                st.session_state.page = "login"
                                st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Registration failed: {e}")
                    finally:
                        db.close()

        if st.button("⬅️ Back to Home Screen", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

def login_page():
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    with center_content:
        st.header("🔑 Account Sign In")
        if not DB_OK:
            st.error("Database connection is not available. Login is disabled.")
            if st.button("Back to Home", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
            return

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In", use_container_width=True)
            
            if submitted:
                db = SessionLocal()
                try:
                    user = db.query(User).filter_by(username=username).first()
                    client = get_client_info()
                    if user:
                        stored_hash = get_user_password_value(user)
                        if stored_hash and bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                            # Populate target metrics to global session state variables cleanly
                            st.session_state.user_id = getattr(user, 'id', None)
                            st.session_state.username = getattr(user, 'username', username)
                            st.session_state.email = getattr(user, 'email', 'Not Specified')
                            st.session_state.company_name = getattr(user, 'company_name', 'Not Specified') or 'Not Specified'
                            st.session_state.position = getattr(user, 'position', 'Not Specified') or 'Not Specified'
                            st.session_state.company_type = getattr(user, 'company_type', 'Not Specified')
                            st.session_state.last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            add_log(db,
                                    user_type="user",
                                    user_id=getattr(user, 'id', None),
                                    username=getattr(user, 'username', username),
                                    email=getattr(user, 'email', None),
                                    login_status="success",
                                    ip_address=client["ip"],
                                    user_agent=client["user_agent"]
                                    )
                            
                            # --- INSTANT CROSS-PAGE REDIRECTION TO DASHBOARD.PY ---
                            # Note: If dashboard.py sits in a nested subdirectory like pages/,
                            # use st.switch_page("pages/dashboard.py") instead.
                            try:
                                st.switch_page("dashboard.py")
                            except Exception:
                                # Fallback if folder placement dictates explicit multi-page directory mapping
                                st.switch_page("pages/dashboard.py")
                        else:
                            add_log(db, user_type="user", username=username, login_status="failed", ip_address=client["ip"], user_agent=client["user_agent"], failure_reason="Invalid credentials")
                            st.error("Invalid username or password")
                    else:
                        add_log(db, user_type="user", username=username, login_status="failed", ip_address=client["ip"], user_agent=client["user_agent"], failure_reason="User not found")
                        st.error("Invalid username or password")
                except Exception as e:
                    st.error(f"Login error: {e}")
                finally:
                    db.close()

        if st.button("⬅️ Back to Home Screen", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

# ---------- Routing Controller ----------
def router():
    render_sidebar_status()
    page = st.session_state.page
    
    if page == "home":
        home_page()
    elif page == "register":
        register_page()
    elif page == "login":
        login_page()
    else:
        st.session_state.page = "home"
        home_page()

if __name__ == "__main__":
    router()