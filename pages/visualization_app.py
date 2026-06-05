"""
Visualization Dashboard Page
Accessible only after successful login
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import psycopg2
from psycopg2 import Error

# Page configuration
st.set_page_config(page_title="Visualization Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'forecast_DB',
    'user': 'postgres',
    'password': 'wense2703'
}

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.error("❌ You must log in first!")
    st.info("👉 Please go back to the login page")
    if st.button("🔐 Go to Login"):
        st.switch_page("registration_app.py")
    st.stop()

# Sidebar - User Details and Services
with st.sidebar:
    st.markdown("---")
    st.subheader("👤 User Details")
    
    # Get user info from session
    user_name = st.session_state.user_info.get('username', 'User')
    user_email = st.session_state.user_info.get('email', 'N/A')
    user_id = st.session_state.user_info.get('id', 'N/A')
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("👤")
    with col2:
        st.markdown(f"**{user_name}**")
    
    st.caption(f"🆔 ID: {user_id}")
    st.caption(f"📧 {user_email}")
    login_time = st.session_state.get('login_time', datetime.now())
    st.caption(f"📅 Logged in: {login_time.strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    st.subheader("🔗 Services")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Visualizations", use_container_width=True):
            st.info("You are here!")
    with col2:
        if st.button("📈 Forecasts", use_container_width=True):
            st.info("Coming soon...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analysis", use_container_width=True):
            st.info("Coming soon...")
    with col2:
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Coming soon...")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state.logged_in = False
        st.session_state.user_info = None
        st.success("✅ Logged out successfully!")
        st.switch_page("registration_app.py")

# Main content
st.title("🎯 Petroleum Price Visualization Dashboard")
st.markdown(f"Welcome, **{user_name}**! 👋")
st.divider()

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Data Points", "1,250", "+12%")
with col2:
    st.metric("📈 Avg Price", "$85.42", "+2.1%")
with col3:
    st.metric("🔝 Highest", "$92.15", "Jun 2024")
with col4:
    st.metric("🔻 Lowest", "$78.50", "Jan 2024")

st.divider()

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Trends", "📈 Forecasts", "🔍 Analysis", "📋 Data Table"])

with tab1:
    st.subheader("Historical Petroleum Prices")
    
    # Generate sample data
    dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
    prices = 80 + 10 * np.sin(np.arange(365) / 365 * 2 * np.pi) + np.random.normal(0, 2, 365)
    
    df_prices = pd.DataFrame({'Date': dates, 'Price': prices})
    
    # Line chart
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=df_prices['Date'],
        y=df_prices['Price'],
        mode='lines',
        name='Price',
        line=dict(color='#3b82f6', width=2),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)'
    ))
    
    fig_line.update_layout(
        title='Petroleum Price Over Time',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with tab2:
    st.subheader("Price Forecasts")
    
    # Generate sample forecast data
    forecast_dates = pd.date_range(start='2024-06-01', periods=180, freq='D')
    forecast_prices = 85 + 5 * np.sin(np.arange(180) / 180 * 2 * np.pi) + np.random.normal(0, 1.5, 180)
    upper_bound = forecast_prices + 3
    lower_bound = forecast_prices - 3
    
    df_forecast = pd.DataFrame({
        'Date': forecast_dates,
        'Forecast': forecast_prices,
        'Upper': upper_bound,
        'Lower': lower_bound
    })
    
    # Forecast chart with confidence interval
    fig_forecast = go.Figure()
    
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['Date'],
        y=df_forecast['Upper'],
        fill=None,
        mode='lines',
        line_color='rgba(255,0,0,0)',
        showlegend=False
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['Date'],
        y=df_forecast['Lower'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(255,0,0,0)',
        name='Confidence Interval',
        fillcolor='rgba(255, 0, 0, 0.2)'
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=df_forecast['Date'],
        y=df_forecast['Forecast'],
        mode='lines',
        name='Forecast',
        line=dict(color='#ef4444', width=2)
    ))
    
    fig_forecast.update_layout(
        title='6-Month Price Forecast',
        xaxis_title='Date',
        yaxis_title='Forecasted Price (USD)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_forecast, use_container_width=True)

with tab3:
    st.subheader("Price Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution chart
        fig_dist = px.histogram(df_prices, x='Price', nbins=30, 
                               title='Price Distribution')
        fig_dist.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Box plot
        fig_box = px.box(df_prices, y='Price', title='Price Box Plot')
        fig_box.update_layout(template='plotly_white', height=400)
        st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    st.subheader("Price Data Table")
    
    # Display sample data
    st.dataframe(
        df_prices.tail(30).reset_index(drop=True),
        use_container_width=True,
        height=400
    )
    
    # Download option
    csv = df_prices.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv.encode('utf-8'),
        file_name=f"petroleum_prices_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

st.divider()

# Additional statistics
st.subheader("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Mean Price**: ${df_prices['Price'].mean():.2f}
    **Median Price**: ${df_prices['Price'].median():.2f}
    """)

with col2:
    st.info(f"""
    **Std Deviation**: ${df_prices['Price'].std():.2f}
    **Min Price**: ${df_prices['Price'].min():.2f}
    """)

with col3:
    st.info(f"""
    **Max Price**: ${df_prices['Price'].max():.2f}
    **Price Range**: ${df_prices['Price'].max() - df_prices['Price'].min():.2f}
    """)

st.divider()

# Footer
st.markdown("""
---
**Petroleum Price Forecasting System** © 2026 | Built with Streamlit & Prophet  
Last Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
