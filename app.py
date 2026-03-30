import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Secure APAC Support Portal", 
    layout="wide", 
    page_icon="🔐"
)

# 2. LOGIN LOGIC (Hides dashboard until password is correct)
def check_password():
    """Returns True if the user has entered the correct password."""
    if "password_correct" not in st.session_state:
        # Show login screen
        st.markdown("<h2 style='text-align: center;'>APAC & Rubrik Operations Center</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            password = st.text_input("Please enter the Security Key", type="password")
            if st.button("Enter Dashboard"):
                # Matches the password you set in Streamlit Secrets
                if password == st.secrets["DASHBOARD_PASSWORD"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Incorrect Password")
        return False
    return True

# 3. SECURE CONTENT (Only runs if password is confirmed)
if check_password():
    # Sidebar logout and status
    st.sidebar.success("✅ Secure Connection Active")
    if st.sidebar.button("Logout"):
        del st.session_state["password_correct"]
        st.rerun()

    st.title("🌏 APAC Support & Rubrik Report")
    
    try:
        # Establish connection to Google Sheets using Secrets
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Load Data from URLs stored in your Secrets vault
        # Use st.cache_data so it doesn't reload on every click (refreshes every 10 mins)
        @st.cache_data(ttl=600)
        def get_data():
            df_inact = conn.read(spreadsheet=st.secrets["inactivity_url"])
            df_assign = conn.read(spreadsheet=st.secrets["assignment_url"])
            return df_inact, df_assign

        df_inact, df_assign = get_data()

        # --- DASHBOARD LAYOUT ---
        
        # Top Row: Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Inactive Cases (>48h)", len(df_inact))
        m2.metric("Today's Assignments", len(df_assign))
        m3.metric("Last Data Refresh", pd.Timestamp.now().strftime("%H:%M %p"))

        st.divider()

        # Middle Row: Charts and Data
        left, right = st.columns(2)
        
        with left:
            st.subheader("📊 Team Workload Today")
            # Note: Ensure your Google Sheet has a column named 'Engineer' 
            # or update the name below to match your header exactly.
            if 'Engineer' in df_assign.columns:
                st.bar_chart(df_assign['Engineer'].value_counts())
            else:
                st.info("To see a chart, ensure your Assignment sheet has an 'Engineer' column.")
        
        with right:
            st.subheader("⚠️ Critical Inactivity List")
            st.dataframe(df_inact, use_container_width=True)

    except Exception as e:
        st.error("🚨 Configuration Error")
        st.info("Check that your Google Sheet URLs and Password are correctly added to 'Secrets' in Streamlit Cloud.")
        # Only show the raw error for debugging if needed:
        # st.write(e)
