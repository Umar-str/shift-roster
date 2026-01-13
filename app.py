import streamlit as st
import pandas as pd
import io
import re
from brain import RosterAgent

# --- CONFIG ---
SHIFT_REPO = ["Morning", "Evening", "Night", "OFF"]

st.set_page_config(page_title="Roster Lab", layout="wide")

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

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏥 Roster Hub")
    
    with st.expander("👨‍⚕️ Staff Reference", expanded=True):
        # Shifts clearly visible here
        st.info(f"**Allowed Shifts:** {', '.join(SHIFT_REPO)}")
        
        st.markdown("""
        **Doctors & Anesth**
        - Mark (Doc)
        - Shawn (Anesth)
        
        **Surgeons**
        - Axel (Surgeon)
        - Sarah (Surgeon)
        
        **Nursing Staff**
        - Elena, David, Chloe
        - James, Maya, Leo
        """)
    
    st.divider()
    if st.button("🗑️ Reset All Memory"):
        st.session_state.history = []
        st.session_state.latest_draft = ""
        st.rerun()
    
    st.subheader("📜 Version History")
    for i, content in enumerate(reversed(st.session_state.history)):
        v_num = len(st.session_state.history) - i
        with st.expander(f"Version {v_num}"):
            st.text_area("Markdown Code", value=content, height=150, key=f"copy_{i}")
            st.markdown("---")
            st.markdown(content, unsafe_allow_html=True)

# --- MAIN UI ---
st.title("Surgery Unit Roster Lab")
c1, c2, c3 = st.columns(3)
with c1: sys_r = st.text_area("🛠️ System Rules", value="- Exactly 1 OFF day per person.", height=150)
with c2: hard_r = st.text_area("⛔ Hard Rules", value="- Mark works Day shifts.", height=150)
with c3: soft_r = st.text_area("💡 Soft Rules", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate Roster Draft", type="primary", use_container_width=True):
    with st.spinner("AI Generating..."):
        st.session_state.latest_draft = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO
        )

# --- DISPLAY & SAVE ---
if st.session_state.latest_draft:
    st.divider()
    st.subheader("📋 Current Draft Preview")
    
    st.markdown(st.session_state.latest_draft, unsafe_allow_html=True)

    if st.button("💾 Save to Sidebar History", use_container_width=True):
        st.session_state.history.append(st.session_state.latest_draft)
        st.success(f"Version {len(st.session_state.history)} saved!")
        st.rerun()