import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="APAC Support Dashboard", layout="wide")
st.title("🌏 APAC Support Operations Dashboard")

# --- CONNECT TO GOOGLE SHEETS ---
# 1. Open your Google Sheet
# 2. Click "Share" -> "Anyone with the link can view"
# 3. Copy that link and paste it here
INACTIVITY_URL = "PASTE_YOUR_INACTIVITY_SHEET_LINK_HERE"
ASSIGNMENT_URL = "PASTE_YOUR_ASSIGNMENT_SHEET_LINK_HERE"

conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=600) # Data refreshes every 10 mins
def load_data():
    df_inact = conn.read(spreadsheet=INACTIVITY_URL)
    df_assign = conn.read(spreadsheet=ASSIGNMENT_URL)
    return df_inact, df_assign

try:
    df_inact, df_assign = load_data()

    # KPI Row
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Inactive Cases", len(df_inact))
    kpi2.metric("Today's Assignments", len(df_assign))

    # Visuals Row
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Case Assignment")
        # Update 'Engineer' to match your column name exactly
        st.bar_chart(df_assign['Engineer'].value_counts())
    
    with col2:
        st.subheader("Inactivity List")
        st.dataframe(df_inact, use_container_width=True)

except Exception as e:
    st.warning("Connect your Google Sheets by updating the URLs in the code!")