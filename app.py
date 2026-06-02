import streamlit as st
import pandas as pd
import numpy as np
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# read data
df=pd.read_csv('DATASETS/new_dataset.csv', parse_dates=['date'])
st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
image = Image.open('DATASETS/enhanced logo.png')
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image, width=100)

html_title = """
<style>
    .title-test {
        font-size: 40px;
        font-weight: bold;
        color: #333333;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
<center><h1 class="title-test">Logistics Details Dashboard</h1></center>
"""

with col2:
    st.markdown(html_title, unsafe_allow_html=True)
    
col3, col4, col5 = st.columns([0.1,0.45,0.45])
with col3:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"last updated: \n {box_date}")
    
with col4:
    fig = px.bar(df, x='date', y='price', labels={'date': 'Date', 'price': 'Price'},
                 title='Price Over Time', hover_data=['date', 'price'],
                 template='gridon', height=500)
    st.plotly_chart(fig, use_container_width=True)
   
_, view1, dwn1, view2, dwn2 = st.columns([0.15,0.20,0.20,0.20,0.20])
with view1:
    expander = st.expander(" Petroleum prices (Max per Year)")
    df['year'] = df['date'].dt.year
    yearly_max = df.groupby('year')['price'].max().reset_index()
    expander.dataframe(yearly_max, use_container_width=True, hide_index=True)
    
with dwn1:
    st.download_button("Get Data", data=yearly_max.to_csv().encode('utf-8'),
                       file_name="petroleum_prices(2010-2025).csv", mime='text/csv' 
                       )
    
with col5:
    fig1 = px.line(df, x='date', y='price', labels={'date': 'Date', 'price': 'Price'},
                 title='Price Over Time', hover_data=['date', 'price'],
                 template='gridon', height=500)
    st.plotly_chart(fig1, use_container_width=True)