"""
Streamlit Login Page
Petroleum Price Forecasting System
"""

import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Login - Petroleum Forecasting",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        h1 {
            color: #1e3a8a;
            text-align: center;
            font-weight: bold;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            padding: 2.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .stButton > button {
            background-color: #3b82f6;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #1e3a8a;
        }
        .footer-link {
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e0e0e0;
        }
        .footer-link a {
            color: #3b82f6;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'forecast_DB',
    'user': 'postgres',
    'password': 'wense2703'
}

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def get_db_connection():
    """Establish database connection"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"❌ Database connection error: {e}")
        return None


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def login_user(connection, username, password):
    """Authenticate user login"""
    try:
        cursor = connection.cursor()
        password_hash = hash_password(password)
        
        cursor.execute("""
            SELECT id, username, email FROM users 
            WHERE username = %s AND password_hash = %s
        """, (username, password_hash))
        
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return True, {"id": result[0], "username": result[1], "email": result[2]}
        else:
            return False, "Invalid username or password"
    
    except Error as e:
        cursor.close()
        return False, f"Login error: {str(e)}"


# Check if already logged in
if st.session_state.logged_in:
    st.switch_page("pages/visualization_app.py")

# Main content
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown("# 🔐")

st.markdown("<h1>Login to Your Account</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; margin-bottom: 2rem;'>Enter your credentials to access the dashboard</p>", unsafe_allow_html=True)

# Login form container
col1, col2, col3 = st.columns([1, 1.5, 1])

with col2:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input(
            "👤 Username",
            placeholder="Enter your username",
            help="Your registered username"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        remember_me = st.checkbox("Remember me on this device")
        
        login_button = st.form_submit_button(
            "🔓 Login",
            use_container_width=True
        )
        
        if login_button:
            if not username or not password:
                st.error("❌ Please enter both username and password")
            else:
                with st.spinner("🔍 Verifying credentials..."):
                    try:
                        connection = get_db_connection()
                        if connection:
                            try:
                                success, result = login_user(connection, username, password)
                                if success:
                                    st.session_state.logged_in = True
                                    st.session_state.user_info = result
                                    st.session_state.login_time = datetime.now()
                                    st.success(f"✅ Welcome back, {result['username']}!")
                                    st.info("🚀 Redirecting to dashboard...")
                                    st.sleep(1)
                                    st.switch_page("pages/visualization_app.py")
                                else:
                                    st.error(f"❌ {result}")
                            finally:
                                if connection and not connection.closed:
                                    connection.close()
                    except Exception as e:
                        st.error(f"❌ Login failed: {str(e)}")
    
    # Footer links
    st.markdown("""
    <div class="footer-link">
        <p style="color: #666; margin: 0;">Don't have an account?</p>
        <p style="color: #666; margin: 0.5rem 0;">
            <a href="#" onclick="window.location.href='?page=register'">Create one now →</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("pages/home.py")

with col3:
    if st.button("📝 Register Here →", use_container_width=True):
        st.switch_page("pages/register.py")

st.divider()

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    **Common Issues:**
    
    - **Forgot your password?** Contact admin support
    - **Account not yet created?** Go to the [Registration Page](pages/register.py)
    - **Still having issues?** Check your credentials or try again later
    
    **Tips:**
    - Make sure Caps Lock is OFF
    - Check your username and password spelling
    - Use the correct database credentials
    """)
