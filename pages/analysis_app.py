"""
pages/analysis_app.py - Sub-page that shares the forecast data directly
from the main application state and renders a highly visual layout using clean parsing.
Secured with authentication guards mapped from index.py routing state.
"""
import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime
import plotly.graph_objects as go
# Official modern SDK: pip install google-genai
from google import genai
from google.genai import types

# ----------------------------------------------------
# 1. CONSTANTS & CONFIGURATION
# ----------------------------------------------------
GEMINI_API_KEY = "AQ.Ab8RN6Kwf394VK9wm5L5_ZnI3RS4TqtBpaW6JWU5ATsK9tMmVQ"

# --- MUST BE THE VERY FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Sales Analysis", layout="wide")

# --- SECURITY & AUTHENTICATION GUARD CLAUSE ---
# Ensures an unauthorized user cannot bypass index.py entry criteria
if "user_id" not in st.session_state or st.session_state.user_id is None:
    left_margin, center_content, right_margin = st.columns([0.2, 3.6, 0.2])
    with center_content:
        st.error("🛑 Security Access Denied. Please sign in via the portal to access live analysis briefs.")
        st.page_link("pages/index.py", label="⬅️ Back to Home Screen", use_container_width=True)
    st.stop()

st.title("⛽ Petrol Price Analysis & Operations Assistant")

# Verify if data exists in the shared session state
if 'forecast_df' not in st.session_state:
    st.warning("⚠️ No shared forecast data found. Please view the main 'Petroleum Price Forecasting Dashboard' first to initialize the model metrics.")
    st.stop()

# Retrieve shared data from memory
forecast = st.session_state['forecast_df']
metadata = st.session_state['metadata']
forecast_months = st.session_state['forecast_months']

# Compute current month properties
current_time = datetime.now()
current_month_str = current_time.strftime("%B %Y")

# Filter future records for visualization
forecast_data = forecast[forecast['ds'] > metadata['last_date']]

# Extract current month's metric
current_month_row = forecast[
    (forecast['ds'].dt.year == current_time.year) & 
    (forecast['ds'].dt.month == current_time.month)
]

# Display initial top line indicator cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Analysis Target Month", current_month_str)
with col2:
    if not current_month_row.empty:
        predicted_price = round(current_month_row['yhat'].values[0], 2)
        st.metric("Model Predicted Petrol Price", f"TZS {predicted_price:,}")
    else:
        predicted_price = None
        st.metric("Model Predicted Petrol Price", "Out of Bounds")
with col3:
    st.metric("Visual Horizon (Shared From Slider)", f"{forecast_months} months")

st.divider()

# Plot 1: Visualizing forecasted results into a Bar Graph
st.subheader("📊 Forecasted Petrol Price Breakdown")
fig = go.Figure()

fig.add_trace(go.Bar(
    x=forecast_data['ds'].dt.strftime('%b %Y'),
    y=forecast_data['yhat'],
    name='Forecasted Price',
    marker_color='rgb(230, 126, 34)', 
    error_y=dict(
        type='data',
        symmetric=False,
        array=forecast_data['yhat_upper'] - forecast_data['yhat'],
        arrayminus=forecast_data['yhat'] - forecast_data['yhat_lower'],
        visible=True,
        color='rgba(44, 62, 80, 0.4)'
    )
))

fig.update_layout(
    title=f'Upcoming {forecast_months}-Month Petrol Price Projections with Uncertainty Margins',
    xaxis_title='Timeline',
    yaxis_title='Price (TZS)',
    template='plotly_white',
    height=400,
    barmode='group'
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Gemini AI Advisory Section
st.subheader("🤖 Live Market Comparison & Operator Insights")

if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE" or not GEMINI_API_KEY:
    st.warning("⚠️ Please open the code file and replace `'YOUR_GEMINI_API_KEY_HERE'` with your actual Gemini API key.")
else:
    if predicted_price is None:
        st.warning("Could not match the current system month against your model's forecast dates.")
    else:
        with st.spinner("Analyzing current EWURA data and generating visual brief..."):
            import time
            
            max_retries = 3
            retry_delay = 2 
            response_json = None
            
            for attempt in range(max_retries):
                try:
                    client = genai.Client(api_key=GEMINI_API_KEY)
                    
                    prompt_content = f"""
                    You are a senior downstream energy analyst specializing in East African oil markets. 
                    Today's date is {current_time.strftime('%B %d, %Y')}.
                    
                    Perform the following specific tasks based strictly on PETROL (MSP/Gasoline) prices only (DO NOT mention Diesel prices):
                    1. Find the official EWURA (Energy and Water Utilities Regulatory Authority) cap retail pump price for Petrol in Tanzania (Dar es Salaam indicator) for this month ({current_month_str}).
                    2. Calculate the difference between that actual price and our model's prediction of {predicted_price} TZS.
                    3. Provide exactly 3 concise, high-impact explanations for any fluctuations or variances. Use STRONG, data-driven bullet labels.
                    4. Give clear operational action strategies for petrol station and logistics operators to handle this current pricing structure.
                    
                    CRITICAL: You must provide your entire response as a single, valid JSON block inside markdown code tags like this:
                    ```json
                    {{
                        "ewura_cap_price": 4086.00,
                        "effective_date": "June 3, 2026",
                        "variance": 814.43,
                        "variance_direction": "HIGHER",
                        "drivers": [
                            {{"title": "Middle East Conflict", "short_desc": "Geopolitical instability disrupts production, storage, transport. Affects global premiums."}},
                            {{"title": "Strait of Hormuz Closure", "short_desc": "Vital trade corridor closure. Increases ocean freight and insurance costs."}},
                            {{"title": "TZS Depreciation", "short_desc": "Tanzanian Shilling weakening against USD. Elevates imported petrol costs."}}
                        ],
                        "strategies": [
                            {{"title": "Inventory Optimization", "points": ["Just-in-Time strategy", "Minimize holding costs", "Sufficient stock for demand"]}},
                            {{"title": "Fleet Efficiency", "points": ["Invest in fuel-efficient vehicles", "Optimize routes", "Strict driving practices"]}},
                            {{"title": "Market Surveillance", "points": ["Track global crude prices", "Monitor refined benchmarks", "Anticipate future adjustments"]}},
                            {{"title": "Hedge Exposure", "points": ["Hedge fuel costs (large operators)", "Mitigate exchange rate risk", "Lock in future prices"]}}
                        ]
                    }}
                    ```
                    Do not put any text before or after the markdown code block.
                    """
                    
                    # Execute API request with Search Grounding enabled (No mime_type lock)
                    api_call = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_content,
                        config=types.GenerateContentConfig(
                            tools=[{"google_search": {}}],
                            temperature=0.1
                        )
                    )
                    
                    # Regex extract to clean text inside ```json ... ``` blocks
                    match = re.search(r'```json\s*(.*?)\s*```', api_call.text, re.DOTALL)
                    json_string = match.group(1) if match else api_call.text
                    
                    response_json = json.loads(json_string.strip())
                    break 
                    
                except Exception as e:
                    if ("503" in str(e) or "400" in str(e)) and attempt < max_retries - 1:
                        st.warning(f"Retrying connection context... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2 
                    else:
                        st.error(f"An error occurred while communicating with Gemini AI: {e}")
                        break
            
            # --- VISUAL RENDERING PIPELINE ---
            if response_json:
                try:
                    ewura_val = float(response_json.get("ewura_cap_price", 0.0))
                    variance_val = float(response_json.get("variance", 0.0))
                    var_direction = response_json.get("variance_direction", "HIGHER")
                    eff_date = response_json.get("effective_date", "N/A")
                    
                    st.markdown("### 📋 Real-World Cap Analysis vs. Model Projections")
                    
                    # Row 1: Dashboard Cards
                    card_col1, card_col2, card_col3 = st.columns([2, 1.5, 2])
                    
                    with card_col1:
                        st.markdown(f"""
                        <div style="background-color: #f1f7fe; border-left: 5px solid #1a76df; padding: 20px; border-radius: 8px;">
                            <span style="color: #1a76df; font-weight: bold; font-size: 1.1em;">TZ$ EWURA CAP PRICE</span>
                            <h2 style="margin: 5px 0; color: #111;">TZS {ewura_val:,.2f}</h2>
                            <p style="margin: 0; font-size: 0.85em; color: #555;"><b>Port:</b> Dar es Salaam<br><b>Effective:</b> {eff_date}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with card_col2:
                        # Recreating the Variance Gauge with Plotly
                        fig_gauge = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = variance_val,
                            number = {'prefix': "TZS ", 'font': {'size': 20}},
                            title = {'text': f"VARIANCE ({var_direction})", 'font': {'size': 12, 'color': '#777'}},
                            gauge = {
                                'axis': {'range': [None, max(variance_val * 2, 100)], 'tickwidth': 1},
                                'bar': {'color': "#d9534f"},
                                'steps': [
                                    {'range': [0, variance_val], 'color': "#f9f9f9"},
                                    {'range': [variance_val, max(variance_val * 2, 100)], 'color': "#ffebee"}
                                ]
                            }
                        ))
                        fig_gauge.update_layout(height=140, margin=dict(l=20, r=20, t=40, b=10))
                        st.plotly_chart(fig_gauge, use_container_width=True, key="gauge_chart")
                        
                    with card_col3:
                        st.markdown(f"""
                        <div style="background-color: #f9f9f9; border-left: 5px solid #777; padding: 20px; border-radius: 8px;">
                            <span style="color: #555; font-weight: bold; font-size: 1.1em;">📈 FORECASTED MODEL</span>
                            <h2 style="margin: 5px 0; color: #333;">TZS {predicted_price:,.2f}</h2>
                            <p style="margin: 0; font-size: 0.85em; color: #555;"><br><b>Target Month:</b> {current_month_str}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    st.write("")
                    st.markdown("### 🔍 Key Market Fluctuation Drivers")
                    
                    # Row 2: Driver Sub-cards
                    drivers = response_json.get("drivers", [])
                    if drivers:
                        d_cols = st.columns(len(drivers))
                        for idx, driver in enumerate(drivers):
                            with d_cols[idx]:
                                st.markdown(f"""
                                <div style="background-color: #ffffff; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); border: 1px solid #eef0f2; padding: 15px; border-radius: 8px; min-height: 140px;">
                                    <h5 style="margin: 0 0 8px 0; color: #e67e22;">💡 {driver.get('title')}</h5>
                                    <p style="margin: 0; font-size: 0.88em; color: #555; line-height: 1.4;">{driver.get('short_desc')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                    st.write("")
                    st.markdown("### ✅ Professional Operational Strategy")
                    
                    # Row 3: Actionable Cards
                    strategies = response_json.get("strategies", [])
                    if strategies:
                        s_cols = st.columns(len(strategies))
                        for idx, strat in enumerate(strategies):
                            with s_cols[idx]:
                                bullet_points = "".join([f"<li style='margin-bottom:4px;'>{pt}</li>" for pt in strat.get('points', [])])
                                st.markdown(f"""
                                <div style="background-color: #fff; border-top: 4px solid #2ecc71; box-shadow: 0px 2px 6px rgba(0,0,0,0.04); padding: 15px; border-radius: 4px; min-height: 180px;">
                                    <strong style="color: #333; font-size: 1em;">🛠️ {strat.get('title')}</strong>
                                    <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 0.88em; color: #444;">
                                        {bullet_points}
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                                
                except Exception as parse_err:
                    st.error(f"Visualization formatting error: {parse_err}")
                    st.text(api_call.text)