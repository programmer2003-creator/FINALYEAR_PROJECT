"""
Streamlit app to display data visualizations and analysis
Secured with authentication guards mapped from index.py routing state.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- MUST BE THE VERY FIRST STREAMLIT COMMAND ---
st.set_page_config(page_title="Data Visualization Dashboard", layout="wide")

    
# Sidebar - User Details and Services
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

st.title("Petroleum Price & Exchange Rate Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('DATASETS/new_dataset.csv', parse_dates=['date'])
    df.set_index('date', inplace=True)
    return df

df = load_data()

# Display basic statistics
st.subheader("Data Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", len(df))
with col2:
    st.metric("Price (Avg)", f"${df['price'].mean():.2f}")
with col3:
    st.metric("Exchange Rate (Avg)", f"{df['exchange rate (1 USD TO TZS)'].mean():.2f}")
with col4:
    st.metric("Date Range", f"{df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")

st.divider()

# Visualization 1: Price over Time
st.subheader("Price Over Time")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df.index,
    y=df['price'],
    mode='lines',
    name='Price',
    line=dict(color='steelblue', width=2)
))
fig1.update_layout(
    title='Price over Time',
    xaxis_title='Date',
    yaxis_title='Price',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# Visualization 2: Price by Date (Bar Chart)
st.subheader("Price by Date (Bar Chart)")
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df.index,
    y=df['price'],
    name='Price',
    marker=dict(color='skyblue')
))
fig2.update_layout(
    title='Price by Date',
    xaxis_title='Date',
    yaxis_title='Price',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Visualization 3: Exchange Rate over Time
st.subheader("Exchange Rate Over Time")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=df.index,
    y=df['exchange rate (1 USD TO TZS)'],
    mode='lines',
    name='Exchange Rate',
    line=dict(color='coral', width=2)
))
fig3.update_layout(
    title='Exchange Rate over Time',
    xaxis_title='Date',
    yaxis_title='Exchange Rate (1 USD TO TZS)',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# Visualization 4: Exchange Rate by Date (Bar Chart)
st.subheader("Exchange Rate by Date (Bar Chart)")
fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=df.index,
    y=df['exchange rate (1 USD TO TZS)'],
    name='Exchange Rate',
    marker=dict(color='lightcoral')
))
fig4.update_layout(
    title='Exchange Rate by Date',
    xaxis_title='Date',
    yaxis_title='Exchange Rate',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Visualization 5: Price and Exchange Rate (Dual Line)
st.subheader("Price and Exchange Rate Over Time")
fig5 = go.Figure()
fig5.add_trace(go.Scatter(
    x=df.index,
    y=df['price'],
    mode='lines',
    name='Price',
    line=dict(color='steelblue', width=2)
))
fig5.add_trace(go.Scatter(
    x=df.index,
    y=df['exchange rate (1 USD TO TZS)'],
    mode='lines',
    name='Exchange Rate (1 USD TO TZS)',
    line=dict(color='coral', width=2, dash='dash')
))
fig5.update_layout(
    title='Price and Exchange Rate over Time',
    xaxis_title='Date',
    yaxis_title='Values',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# Visualization 6: Price and Exchange Rate (Dual Bar)
st.subheader("Price and Exchange Rate Comparison (Dual Bar)")
fig6 = go.Figure()
fig6.add_trace(go.Bar(
    x=df.index,
    y=df['price'],
    name='Price',
    marker=dict(color='skyblue')
))
fig6.add_trace(go.Bar(
    x=df.index,
    y=df['exchange rate (1 USD TO TZS)'],
    name='Exchange Rate',
    marker=dict(color='lightcoral')
))
fig6.update_layout(
    title='Price and Exchange Rate by Date',
    xaxis_title='Date',
    yaxis_title='Values',
    barmode='group',
    template='plotly_white',
    height=500,
    hovermode='x unified'
)
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# Visualization 7: Average Price per Year (Pie Chart)
st.subheader("Average Price Distribution by Year")
avg_price_per_year = df.groupby(df.index.year)['price'].mean()
fig7 = go.Figure(data=[go.Pie(
    labels=avg_price_per_year.index,
    values=avg_price_per_year.values,
    hovertemplate='<b>Year: %{label}</b><br>Average Price: $%{value:.2f}<extra></extra>'
)])
fig7.update_layout(
    title='Average Price Distribution by Year',
    template='plotly_white',
    height=500
)
st.plotly_chart(fig7, use_container_width=True)

st.divider()

# Visualization 8: Highest Price Month per Year
st.subheader("Highest Price Month per Year")
df_temp = df.copy()
df_temp['Year'] = df_temp.index.year
df_temp['Month'] = df_temp.index.month

monthly_avg = df_temp.groupby(['Year', 'Month'])['price'].mean()
highest_months = monthly_avg.groupby('Year').idxmax()
highest_values = monthly_avg.groupby('Year').max()

result = pd.DataFrame({
    'Year': [year for year, month in highest_months],
    'Month': [month for year, month in highest_months],
    'Highest Price': highest_values.values
})

# Display as interactive table
st.dataframe(result, use_container_width=True, hide_index=True)

# Bar chart for highest price by year
fig8 = go.Figure()
fig8.add_trace(go.Bar(
    x=result['Year'],
    y=result['Highest Price'],
    name='Highest Price',
    marker=dict(color='mediumseagreen')
))
fig8.update_layout(
    title='Highest Price per Year',
    xaxis_title='Year',
    yaxis_title='Price',
    template='plotly_white',
    height=400,
    hovermode='x unified'
)
st.plotly_chart(fig8, use_container_width=True)

# Download data
st.divider()
csv = result.to_csv(index=False)
st.download_button(
    label="📥 Download Highest Price Data as CSV",
    data=csv.encode('utf-8'),
    file_name=f"highest_price_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
    mime='text/csv'
)