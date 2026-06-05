"""
Streamlit Registration Page
Petroleum Price Forecasting System
"""

import streamlit as st
import psycopg2
from psycopg2 import Error
import hashlib
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Register - Petroleum Forecasting",
    page_icon="📝",
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
        .register-container {
            background: white;
            border-radius: 15px;
            padding: 2.5rem;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }
        .stButton > button {
            background-color: #10b981;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            border: none;
            width: 100%;
        }
        .stButton > button:hover {
            background-color: #059669;
        }
        .footer-link {
            text-align: center;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid #e0e0e0;
        }
        .password-requirement {
            font-size: 0.85rem;
            margin: 0.25rem 0;
            padding: 0.25rem;
        }
        .requirement-pass {
            color: #10b981;
        }
        .requirement-fail {
            color: #ef4444;
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


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_strong_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Must be at least 8 characters")
    if not any(char.isupper() for char in password):
        errors.append("Must contain at least one uppercase letter")
    if not any(char.isdigit() for char in password):
        errors.append("Must contain at least one digit")
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
        errors.append("Must contain at least one special character")
    
    return len(errors) == 0, errors


def username_exists(connection, username):
    """Check if username already exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"❌ Database error: {e}")
        return False


def email_exists(connection, email):
    """Check if email already exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except Error as e:
        st.error(f"❌ Database error: {e}")
        return False


def register_user(connection, username, email, password):
    """Register a new user in the database"""
    try:
        cursor = connection.cursor()
        password_hash = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, password_hash, datetime.now(), datetime.now()))
        
        connection.commit()
        cursor.close()
        return True, "Registration successful!"
    
    except Error as e:
        connection.rollback()
        cursor.close()
        return False, f"Registration error: {str(e)}"


# Check if already logged in
if st.session_state.get('logged_in', False):
    st.switch_page("pages/visualization_app.py")

# Main content
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown("# 📝")

st.markdown("<h1>Create Your Account</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; margin-bottom: 2rem;'>Join us and start forecasting petroleum prices</p>", unsafe_allow_html=True)

# Registration form container
col1, col2, col3 = st.columns([1, 1.5, 1])

with col2:
    st.markdown('<div class="register-container">', unsafe_allow_html=True)
    
    with st.form("registration_form"):
        username = st.text_input(
            "👤 Username",
            placeholder="Choose a unique username (3-255 characters)",
            help="Your unique login identifier"
        )
        
        email = st.text_input(
            "📧 Email Address",
            placeholder="your.email@example.com",
            help="We'll use this to verify your account"
        )
        
        password = st.text_input(
            "🔑 Password",
            type="password",
            placeholder="Create a strong password",
            help="Must meet all requirements below"
        )
        
        # Real-time password strength check
        if password:
            is_strong, password_errors = is_strong_password(password)
            
            if is_strong:
                st.success("✅ Password is strong!")
            else:
                st.warning("⚠️ Password requirements:")
                for error in password_errors:
                    st.markdown(f"<div class='password-requirement requirement-fail'>❌ {error}</div>", unsafe_allow_html=True)
        
        password_confirm = st.text_input(
            "🔐 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            help="Must match the password above"
        )
        
        # Password match indicator
        if password and password_confirm:
            if password == password_confirm:
                st.success("✅ Passwords match!")
            else:
                st.error("❌ Passwords do not match")
        
        st.divider()
        
        terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must accept terms to register"
        )
        
        register_button = st.form_submit_button(
            "✅ Create Account",
            use_container_width=True
        )
        
        if register_button:
            # Validation
            errors = []
            
            # Username validation
            if not username:
                errors.append("Username is required")
            elif len(username) < 3:
                errors.append("Username must be at least 3 characters")
            elif len(username) > 255:
                errors.append("Username must not exceed 255 characters")
            elif not username.replace('_', '').isalnum():
                errors.append("Username can only contain letters, numbers, and underscores")
            
            # Email validation
            if not email:
                errors.append("Email is required")
            elif not is_valid_email(email):
                errors.append("Invalid email format")
            
            # Password validation
            if not password:
                errors.append("Password is required")
            else:
                is_strong, password_errors = is_strong_password(password)
                if not is_strong:
                    for pe in password_errors:
                        errors.append(f"Password: {pe}")
            
            # Confirm password
            if password != password_confirm:
                errors.append("Passwords do not match")
            
            # Terms agreement
            if not terms:
                errors.append("You must agree to the terms to register")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Check if user exists and register
                try:
                    connection = get_db_connection()
                    if connection:
                        try:
                            if username_exists(connection, username):
                                st.error("❌ Username already exists. Please choose a different one.")
                            elif email_exists(connection, email):
                                st.error("❌ Email already registered. Please use a different email or log in.")
                            else:
                                with st.spinner("Creating your account..."):
                                    success, message = register_user(connection, username, email, password)
                                    if success:
                                        st.success(f"✅ {message}")
                                        st.balloons()
                                        st.info("👉 Redirecting to login page...")
                                        st.sleep(1.5)
                                        st.switch_page("pages/login.py")
                                    else:
                                        st.error(message)
                        finally:
                            if connection and not connection.closed:
                                connection.close()
                except Exception as e:
                    st.error(f"❌ Registration failed: {str(e)}")
    
    # Footer links
    st.markdown("""
    <div class="footer-link">
        <p style="color: #666; margin: 0;">Already have an account?</p>
        <p style="color: #666; margin: 0.5rem 0;">
            <a href="pages/login.py">Log in here →</a>
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
    if st.button("🔐 Login Here →", use_container_width=True):
        st.switch_page("pages/login.py")

st.divider()

# Password requirements info
with st.expander("🔐 Password Requirements"):
    st.markdown("""
    Your password must include:
    - ✅ **At least 8 characters** - Longer passwords are more secure
    - ✅ **Uppercase letter** - At least one A-Z
    - ✅ **Number** - At least one 0-9
    - ✅ **Special character** - At least one !@#$%^&*()_+-=[]{}|;:,.<>?
    
    **Examples of strong passwords:**
    - `MyPassword123!`
    - `Forecast@2026`
    - `P3trol$Forecast`
    """)
