"""
Streamlit Landing/Welcome Page - Main Entry Point
Petroleum Price Forecasting System
"""

import streamlit as st

# Page configuration - THIS IS NOW THE ENTRY POINT
st.set_page_config(
    page_title="Petroleum Price Forecasting - Welcome",
    page_icon="🛢️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

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
            color: white;
            text-align: center;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .welcome-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        .feature-box {
            background: rgba(255, 255, 255, 0.95);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #3b82f6;
        }
        .stButton > button {
            font-weight: bold;
            border-radius: 8px;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# Check if already logged in
if st.session_state.get('logged_in', False):
    st.switch_page("pages/visualization_app.py")

# Main content
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown("# 🛢️")

st.markdown("<h1>Petroleum Price Forecasting System</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="welcome-card">
        <h2 style="color: #1e3a8a; margin-top: 0;">Welcome! 👋</h2>
        <p style="color: #666; font-size: 1.1rem;">
            Harness the power of advanced forecasting to predict petroleum prices with confidence.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Features
st.markdown("<h3 style='text-align: center; color: white;'>✨ Why Choose Our Platform?</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-box">
        <h4 style="color: #3b82f6;">📊 Advanced Analytics</h4>
        <p style="color: #666; font-size: 0.95rem;">
            Visualize historical data and trends with interactive charts
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-box">
        <h4 style="color: #3b82f6;">🔮 Accurate Forecasts</h4>
        <p style="color: #666; font-size: 0.95rem;">
            Prophet-powered predictions with confidence intervals
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-box">
        <h4 style="color: #3b82f6;">🔒 Secure & Reliable</h4>
        <p style="color: #666; font-size: 0.95rem;">
            Enterprise-grade security with PostgreSQL database
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# Authentication buttons
st.markdown("<h3 style='text-align: center; color: white;'>Get Started</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 0.5, 1])

with col1:
    if st.button("🔑 Login", use_container_width=True, key="btn_login"):
        st.switch_page("pages/login.py")

with col3:
    if st.button("📝 Register", use_container_width=True, key="btn_register"):
        st.switch_page("pages/register.py")

st.divider()

# Footer
st.markdown("""
<div style="text-align: center; color: white; margin-top: 3rem;">
    <p><strong>Petroleum Price Forecasting System</strong></p>
    <p style="font-size: 0.9rem; opacity: 0.8;">© 2026 | All rights reserved</p>
    <p style="font-size: 0.85rem; opacity: 0.7;">Powered by Python • Streamlit • Prophet • PostgreSQL</p>
</div>
""", unsafe_allow_html=True)
