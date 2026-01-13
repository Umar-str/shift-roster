import streamlit as st
from brain import RosterAgent

# 1. Page Configuration
st.set_page_config(page_title="Surgery Roster Lab", layout="wide")

# 2. Initialize Session State (The "Memory")
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        # Connects to the brain.py class
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key not found! Please add GEMINI_API_KEY to Streamlit Secrets.")

if "history" not in st.session_state:
    st.session_state.history = []

if "latest_roster" not in st.session_state:
    st.session_state.latest_roster = ""

# 3. Sidebar: Staff Directory & Session History
with st.sidebar:
    st.title("🏥 Staff Roster")
    st.subheader("Active Personnel")
    st.markdown("""
    - **Mark** (Doctor)
    - **Shawn** (Anesth.)
    - **Axel / Sarah** (Surgeons)
    - **Nurses**: Elena, David, Chloe, James, Maya, Leo
    """)
    
    st.divider()
    st.subheader("📜 Session Memory")
    if st.button("Reset Session"):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()
    
    # Display History items (Newest first)
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.caption("Copy logic from this run:")
            st.text(content[:150] + "...")

# 4. Main Page UI
st.title("Surgery Unit: Weekly Roster Generator")
st.info("Input your constraints below. Gemini 2.5 Flash will account for previous versions in this session.")

c1, c2, c3 = st.columns(3)
with c1:
    sys_r = st.text_area("System Rules", value="- Exactly 1 Holiday (OFF) per person.", height=150)
with c2:
    hard_r = st.text_area("Hard Rules", value="- Mark works Day shifts.\n- Axel is OFF Wednesday.", height=150)
with c3:
    soft_r = st.text_area("Soft Rules", value="- Try to pair James and Chloe.", height=150)

# 5. Execution Button
if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("AI is reasoning through history and rules..."):
        # This calls the function in brain.py
        res = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history
        )
        # Update memory
        st.session_state.latest_roster = res
        st.session_state.history.append(res)

# 6. Output Display
if st.session_state.latest_roster:
    st.divider()
    st.success("✅ Roster Generated. Highlight and copy the table for Excel.")
    # Displays the Markdown table and the compliance report
    st.markdown(st.session_state.latest_roster)