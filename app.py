import streamlit as st
from brain import RosterAgent

st.set_page_config(page_title="Surgery Roster Lab", layout="wide")

# --- Initialize Session State ---
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")

if "history" not in st.session_state:
    st.session_state.history = []
if "latest_roster" not in st.session_state:
    st.session_state.latest_roster = ""

# --- Sidebar: Staff & History ---
with st.sidebar:
    st.title("👨‍⚕️ Staff Directory")
    st.markdown("""
    **Doctors**
    - Mark (Lead)
    - Shawn (Anesth.)
    
    **Surgeons**
    - Axel
    - Sarah
    
    **Nurses**
    - Elena, David, Chloe, 
    - James, Maya, Leo
    """)
    
    st.divider()
    st.subheader("📜 Session History")
    if st.button("Clear Session Memory"):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()
    
    for i, res in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.caption("Click to view previous result")
            st.text(res[:100] + "...") # Preview

# --- Main UI ---
st.title("🏥 Surgery Unit Roster Generator")

c1, c2, c3 = st.columns(3)
with c1:
    sys_r = st.text_area("System Rules", value="- Exactly 1 Holiday (OFF) per person.", height=150)
with c2:
    hard_r = st.text_area("Hard Rules", value="- Mark (Doctor) works Morning shifts.\n- Axel is OFF Wednesday.", height=150)
with c3:
    soft_r = st.text_area("Soft Rules", value="- Try to pair James and Chloe.", height=150)

if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("Analyzing rules and history..."):
        result = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history
        )
        st.session_state.latest_roster = result
        st.session_state.history.append(result)

# --- Output Display ---
if st.session_state.latest_roster:
    st.divider()
    st.success("✨ Roster Generated! Copy the table below directly into Excel.")
    st.markdown(st.session_state.latest_roster)
