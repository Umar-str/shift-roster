import streamlit as st
import pandas as pd
import io
from brain import RosterAgent

st.set_page_config(page_title="Hospital Roster AI", layout="wide")

# Initialize Roster Agent & History
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🏥 Smart Hospital Roster Generator")

# Sidebar for History
with st.sidebar:
    st.header("📜 Roster History")
    if st.button("Clear History"):
        st.session_state.history = []
    for i, entry in enumerate(st.session_state.history):
        st.write(f"Version {i+1}: {entry['timestamp']}")

# Input Layout
col1, col2, col3 = st.columns(3)
with col1:
    sys_rules = st.text_area("System Rules (Mandatory)", value="Min 2 nurses per night shift.")
with col2:
    hard_rules = st.text_area("Hard Rules (Strict)", value="Mark cannot work Mondays.")
with col3:
    soft_rules = st.text_area("Soft Rules (Preferences)", value="Elena prefers mornings.")

if st.button("Generate Roster", type="primary"):
    with st.spinner("Analyzing history and creating new roster..."):
        # Pass history to the agent
        result = st.session_state.roster_agent.generate_roster(
            sys_rules, hard_rules, soft_rules, st.session_state.history
        )
        
        # Save to history
        import datetime
        st.session_state.history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": result
        })
        
        st.markdown(result)

# Export to Excel Section
if st.session_state.history:
    st.divider()
    st.subheader("📥 Export Latest Roster")
    
    # Simple logic to try and parse the MD table for Excel export
    last_roster = st.session_state.history[-1]['content']
    try:
        # Extract table part (crude markdown to list parsing)
        tables = pd.read_html(io.StringIO(last_roster), flavor='bs4')
        if tables:
            df = tables[0]
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Roster')
            
            st.download_button(
                label="Download as Excel",
                data=buffer.getvalue(),
                file_name="hospital_roster.xlsx",
                mime="application/vnd.ms-excel"
            )
    except:
        st.info("Generating exportable table...")