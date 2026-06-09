import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
from prophet import Prophet

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