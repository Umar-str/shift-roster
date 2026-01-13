import streamlit as st
from brain import RosterAgent

st.set_page_config(page_title="Roster Lab", layout="wide")

# Initialize Logic
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key missing! Add GEMINI_API_KEY to your Secrets.")

if "history" not in st.session_state:
    st.session_state.history = []
if "latest_output" not in st.session_state:
    st.session_state.latest_output = ""

st.title("🏥 Surgery Unit Roster Lab")

# Input Fields
c1, c2, c3 = st.columns(3)
with c1:
    sys_r = st.text_area("System Rules", value="- Exactly 1 Holiday (OFF) per person.", height=150)
with c2:
    hard_r = st.text_area("Hard Rules", value="- Mark (Doctor) works Day shifts.", height=150)
with c3:
    soft_r = st.text_area("Soft Rules", value="- Elena prefers mornings.", height=150)

if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("AI is calculating..."):
        res = st.session_state.roster_agent.generate_roster(sys_r, hard_r, soft_r, st.session_state.history)
        st.session_state.latest_output = res
        st.session_state.history.append(res)

# Display Latest Output
if st.session_state.latest_output:
    st.divider()
    st.info("💡 Highlight the table below and press Ctrl+C to copy into Excel.")
    st.markdown(st.session_state.latest_output)

# History Management
with st.sidebar:
    st.header("📜 Session History")
    if st.button("Reset Session"):
        st.session_state.history = []
        st.session_state.latest_output = ""
        st.rerun()
    
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.markdown(content)