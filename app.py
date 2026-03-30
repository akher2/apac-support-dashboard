import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. PAGE SETUP
st.set_page_config(page_title="APAC & Rubrik Support Dashboard", layout="wide")
st.title("🌏 APAC Support Operations")

# 2. THE SECURE CONNECTION
# We are calling the 'nicknames' from the Streamlit Vault (Secrets)
try:
    # Get the URLs from the secret vault
    INACT_URL = st.secrets["inactivity_url"]
    ASSIGN_URL = st.secrets["assignment_url"]

    conn = st.connection("gsheets", type=GSheetsConnection)

    @st.cache_data(ttl=600)
    def load_data():
        # Using the nicknames to pull data
        df_inact = conn.read(spreadsheet=INACT_URL)
        df_assign = conn.read(spreadsheet=ASSIGN_URL)
        return df_inact, df_assign

    df_inact, df_assign = load_data()

    # 3. THE DASHBOARD VISUALS
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Inactive Cases", len(df_inact))
    kpi2.metric("Today's Assignments", len(df_assign))

    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Assignment Breakdown")
        # Ensure 'Engineer' matches your Google Sheet header exactly
        st.bar_chart(df_assign['Engineer'].value_counts())

    with right:
        st.subheader("Detailed Inactivity List")
        st.dataframe(df_inact, use_container_width=True)

except Exception as e:
    st.error("🔒 Security Error: Please add your Google Sheet URLs to the Streamlit Secrets vault.")
    st.info("The code is public, but the data access is currently locked.")
