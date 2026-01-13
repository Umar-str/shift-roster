import streamlit as st
import pandas as pd
import io
from brain import RosterAgent

st.set_page_config(page_title="Hospital Roster AI", layout="wide")

# Initialize Session State
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Missing GEMINI_API_KEY in Secrets!")

if "history" not in st.session_state:
    st.session_state.history = []
if "latest_roster" not in st.session_state:
    st.session_state.latest_roster = None

st.title("🏥 Hospital Shift Roster Lab")

# UI Columns
c1, c2, c3 = st.columns(3)
with c1:
    sys_rules = st.text_area("System Rules", value="- Every person must have exactly 1 Holiday (OFF).", height=150)
with c2:
    hard_rules = st.text_area("Hard Rules", value="- Mark (Doctor) must work all Day shifts.", height=150)
with c3:
    soft_rules = st.text_area("Soft Rules", value="- Prefer Morning shifts for Elena.", height=150)

if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("AI is generating your roster..."):
        result = st.session_state.roster_agent.generate_roster(
            sys_rules, hard_rules, soft_rules, st.session_state.history
        )
        st.session_state.history.append(result)
        st.session_state.latest_roster = result

# Results and Export
if st.session_state.latest_roster:
    st.divider()
    st.markdown(st.session_state.latest_roster)
    
    try:
        # Use pandas to grab the table from markdown
        df_list = pd.read_html(io.StringIO(st.session_state.latest_roster), flavor='bs4')
        if df_list:
            df = df_list[0]
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Roster')
            
            st.download_button(
                label="📥 Download Roster as Excel",
                data=buffer.getvalue(),
                file_name="hospital_roster.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.info("Table found. Adjusting export settings...")

# Sidebar History
with st.sidebar:
    st.subheader("History Log")
    if st.button("Clear Memory"):
        st.session_state.history = []
        st.rerun()