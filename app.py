import streamlit as st
from brain import RosterAgent

# --- Page Config ---
st.set_page_config(page_title="Surgery Roster Lab", layout="wide")

# --- Custom UI Styling (Borders and Spacing) ---
st.markdown("""
    <style>
    /* Add blue borders to text areas */
    .stTextArea textarea {
        border: 2px solid #007BFF !important;
        border-radius: 8px !important;
    }
    /* Card style for columns */
    [data-testid="column"] {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E9ECEF;
    }
    /* Table styling */
    th { background-color: #007BFF !important; color: white !important; }
    </style>
    """, unsafe_ok=True)

# --- Init Logic ---
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Missing GEMINI_API_KEY in Secrets!")

if "history" not in st.session_state:
    st.session_state.history = []
if "latest_roster" not in st.session_state:
    st.session_state.latest_roster = ""

# --- Sidebar ---
with st.sidebar:
    st.title("👨‍⚕️ Staffing Hub")
    st.info("**Personnel List**\n- Mark (Doc)\n- Shawn (Anes)\n- Axel/Sarah (Surg)\n- 6 Nurses")
    st.divider()
    if st.button("Reset Session Memory"):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()
    
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.text(content[:150] + "...")

# --- Main Page ---
st.title("🗓️ Weekly Surgery Unit Roster")

col1, col2, col3 = st.columns(3)

with col1:
    sys_r = st.text_area("🛡️ System Rules", value="- Exactly 1 Holiday (OFF) per person.", height=150)
with col2:
    hard_r = st.text_area("🛑 Hard Rules", value="- Mark works Day shifts.", height=150)
with col3:
    soft_r = st.text_area("✨ Soft Rules", value="- Elena prefers mornings.", height=150)

if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("AI is reasoning..."):
        res = st.session_state.roster_agent.generate_roster(sys_r, hard_r, soft_r, st.session_state.history)
        st.session_state.latest_roster = res
        if "🚨" not in res:
            st.session_state.history.append(res)

# --- Output ---
if st.session_state.latest_roster:
    st.divider()
    st.success("✅ Roster Generated. Copy the table below into Excel.")
    st.markdown(st.session_state.latest_roster)