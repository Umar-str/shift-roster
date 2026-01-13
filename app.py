import streamlit as st
from brain import RosterAgent

# --- CONFIG ---
SHIFT_REPO = ["Morning", "Evening", "Night", "OFF"]

st.set_page_config(page_title="Roster Lab", layout="wide")

# CSS to style the subtext in the table
st.markdown("""
<style>
    .stTextArea textarea { border: 2px solid #007BFF !important; }
    [data-testid="column"] { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; }
    small { color: #6c757d; font-size: 0.85em; display: block; }
    th { background-color: #007BFF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
if "latest_draft" not in st.session_state:
    st.session_state.latest_draft = ""
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])

# --- SIDEBAR: ADDITIVE HISTORY ---
with st.sidebar:
    st.title("📋 Version Control")
    
    if st.button("🗑️ Reset All Memory"):
        st.session_state.history = []
        st.session_state.latest_draft = ""
        st.rerun()
    
    st.divider()
    st.subheader("Saved Rosters")
    # Loops through history and displays them in expandable, copyable boxes
    for i, content in enumerate(reversed(st.session_state.history)):
        version_num = len(st.session_state.history) - i
        with st.expander(f"Version {version_num}", expanded=(i==0)):
            st.text_area("Copy Text:", value=content, height=150, key=f"copy_{i}")
            st.markdown("---")
            st.markdown(content, unsafe_allow_html=True)

# --- MAIN UI ---
st.title("Surgery Unit Roster Lab")
c1, c2, c3 = st.columns(3)
with c1: sys_r = st.text_area("🛡️ System", value="- Exactly 1 OFF day per person.", height=150)
with c2: hard_r = st.text_area("🛑 Hard", value="- Mark works Day shifts.", height=150)
with c3: soft_r = st.text_area("✨ Soft", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate Roster Draft", type="primary", use_container_width=True):
    with st.spinner("AI is applying rules..."):
        res = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO
        )
        st.session_state.latest_draft = res

# --- DISPLAY & SAVE ---
if st.session_state.latest_draft:
    st.divider()
    st.subheader("Current Draft")
    # The table is rendered with HTML enabled for subtext
    st.markdown(st.session_state.latest_draft, unsafe_allow_html=True)

    if st.button("💾 Save to Sidebar History", use_container_width=True):
        # Additive: This appends to the history list
        st.session_state.history.append(st.session_state.latest_draft)
        st.success(f"Version {len(st.session_state.history)} saved successfully!")
        st.rerun()