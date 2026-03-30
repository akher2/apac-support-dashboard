import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. PAGE CONFIG
st.set_page_config(page_title="🌏 APAC Support Portal", layout="wide", page_icon="🔐")

# 2. LOGIN LOGIC
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>APAC & Rubrik Operations Center</h2>", unsafe_allow_value=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            password = st.text_input("Please enter the Security Key", type="password")
            if st.button("Enter Dashboard"):
                if password == st.secrets["DASHBOARD_PASSWORD"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Incorrect Password")
        return False
    return True

# 3. SECURE CONTENT (Only runs if password is correct)
if check_password():
    st.sidebar.success("✅ Secure Connection Active")
    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()

    st.title("🌏 APAC Support & Rubrik Report")
    
    try:
        # Connect to Sheets using Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Pull Data
        df_inact = conn.read(spreadsheet=st.secrets["inactivity_url"])
        df_assign = conn.read(spreadsheet=st.secrets["assignment_url"])

        # Display Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Inactive Cases (>48h)", len(df_inact))
        m2.metric("Today's New Assignments", len(df_assign))
        m3.metric("Last Data Refresh", pd.Timestamp.now().strftime("%H:%M %p"))

        st.divider()

        # Visuals
        left, right = st.columns(2)
        with left:
            st.subheader("📊 Team Workload Today")
            # Replace 'Engineer' with your actual column name
            st.bar_chart(df_assign['Engineer'].value_counts())
        
        with right:
            st.subheader("⚠️ Critical Inactivity List")
            st.dataframe(df_inact, use_container_width=True)

    except Exception as e:
        st.error("🚨 Configuration Error: Ensure your Google Sheet URLs are correct in the Secrets vault.")
