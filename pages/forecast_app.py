"""
Streamlit app to load the saved Prophet model and make predictions
Secured with authentication guards mapped from index.py routing state.
"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from prophet import Prophet

# --- MUST BE THE VERY FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Sales Forecasting", layout="wide")

# --- SECURITY & AUTHENTICATION GUARD CLAUSE ---
# Ensures an unauthorized user cannot bypass index.py entry criteria
if "user_id" not in st.session_state or st.session_state.user_id is None:
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    with center_content:
        st.error("🛑 Security Access Denied. Please sign in via the portal to access model projection features.")
        st.page_link("pages/index.py", label="⬅️ Back to Home Screen", use_container_width=True)
    st.stop()

st.title("Petroleum Price Forecasting Dashboard")

# Check if model exists
if not os.path.exists('prophet_model.json'):
    st.error("Model not found! Please run `save_prophet_model.py` first.")
    st.stop()

# Load model and metadata
@st.cache_resource
def load_model():
    with open('prophet_model.json', 'r') as f:
        model_data = json.load(f)
    
    with open('model_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Reconstruct the Prophet model from JSON data
    training_data = pd.DataFrame(model_data['training_data'])
    training_data['ds'] = pd.to_datetime(training_data['ds'])
    
    model = Prophet(
        interval_width=model_data['params']['interval_width'],
        yearly_seasonality=model_data['params']['yearly_seasonality'],
        weekly_seasonality=model_data['params']['weekly_seasonality'],
        daily_seasonality=model_data['params']['daily_seasonality']
    )
    model.fit(training_data)
    
    return model, metadata

model, metadata = load_model()

# Sidebar for user input

st.sidebar.markdown("---")
st.sidebar.header("Forecasting Parameters")
forecast_months = st.sidebar.slider("Forecast period (months)", 1, 12, 6)

with st.sidebar:
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

# Make forecast
future_dates = model.make_future_dataframe(periods=forecast_months, freq='MS')
forecast = model.predict(future_dates)

# share data with the analysis page
st.session_state['forecast_df'] = forecast
st.session_state['metadata'] = metadata
st.session_state['forecast_months'] = forecast_months

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Training Data Points", metadata['training_rows'])
with col2:
    st.metric("Last Training Date", metadata['last_date'])
with col3:
    st.metric("Forecast Period (months)", forecast_months)

st.divider()

# Plot 1: Forecast with uncertainty
st.subheader("Price Forecast with Confidence Intervals")
fig = go.Figure()

# Add historical data
fig.add_trace(go.Scatter(
    x=forecast[forecast['ds'] <= metadata['last_date']]['ds'],
    y=forecast[forecast['ds'] <= metadata['last_date']]['yhat'],
    name='Historical',
    line=dict(color='blue')
))

# Add forecast
forecast_data = forecast[forecast['ds'] > metadata['last_date']]
fig.add_trace(go.Scatter(
    x=forecast_data['ds'],
    y=forecast_data['yhat'],
    name='Forecast',
    line=dict(color='red', dash='dash')
))

# Add uncertainty interval
fig.add_trace(go.Scatter(
    x=forecast_data['ds'].tolist() + forecast_data['ds'].tolist()[::-1],
    y=forecast_data['yhat_upper'].tolist() + forecast_data['yhat_lower'].tolist()[::-1],
    fill='toself',
    fillcolor='rgba(255, 0, 0, 0.2)',
    line=dict(color='rgba(255, 0, 0, 0)'),
    name='Confidence Interval'
))

fig.update_layout(
    title='Petroleum Price Forecast',
    xaxis_title='Date',
    yaxis_title='Price',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

# Display forecast table
st.subheader("Forecast Data")
forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(forecast_months)
forecast_table.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound']
st.dataframe(forecast_table.reset_index(drop=True), use_container_width=True)

# Download forecast
csv = forecast_table.to_csv(index=False)
st.download_button(
    label="📥 Download Forecast as CSV",
    data=csv.encode('utf-8'),
    file_name=f"forecast_{datetime.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)

st.divider()

# Components
st.subheader("Forecast Components")
fig2 = model.plot_components(forecast)
st.pyplot(fig2, use_container_width=True)