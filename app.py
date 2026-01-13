import streamlit as st
from brain import RosterAgent

st.set_page_config(page_title="Surgery Roster", layout="wide")

# --- Initialize Session ---
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key not found in Streamlit Secrets!")

if "history" not in st.session_state:
    st.session_state.history = []
if "latest_roster" not in st.session_state:
    st.session_state.latest_roster = ""

# --- Sidebar ---
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
    
    # Display History items
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.caption("Expand to view data")
            st.text(content[:150] + "...")

# --- Main Page ---
st.title("Surgery Unit: Weekly Roster Generator")

c1, c2, c3 = st.columns(3)
with c1:
    sys_r = st.text_area("System Rules", value="- Exactly 1 Holiday (OFF) per person.", height=150)
with c2:
    hard_r = st.text_area("Hard Rules", value="- Mark works Day shifts.", height=150)
with c3:
    soft_r = st.text_area("Soft Rules", value="- Elena prefers mornings.", height=150)

if st.button("Generate Roster", type="primary", use_container_width=True):
    with st.spinner("AI is reasoning..."):
        # Pass the history list to the agent
        res = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history
        )
        st.session_state.latest_roster = res
        st.session_state.history.append(res)

if st.session_state.latest_output := st.session_state.latest_roster:
    st.divider()
    st.success("✅ Roster Generated. Highlight and copy the table for Excel.")
    st.markdown(st.session_state.latest_output)