# router app
import streamlit as st

#st.write('#App.py')
#page navigation

pages = [
    st.Page('pages/index.py', title='Home', icon='🏠'),
    st.Page('pages/dashboard.py', title='User Dashboard', icon='👤'),
    st.Page('pages/visualization_app.py', title='Visualization', icon='📊'),
    st.Page('pages/forecast_app.py', title='Forecasting', icon='📈'),
    st.Page('pages/analysis_app.py', title='Analysis', icon='🔍'),

]

pg = st.navigation(pages, position='sidebar', expanded=True)

# running the app
pg.run()