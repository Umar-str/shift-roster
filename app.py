import streamlit as st
import pandas as pd
import io
import re
from brain import RosterAgent

# --- 1. SHIFT REPOSITORY ---
SHIFT_REPO = ["Morning", "Evening", "Night", "OFF"]

st.set_page_config(page_title="Roster Lab", layout="wide")

# CSS to ensure the <small> tag works and the table looks clean
st.markdown("""
<style>
    .stTextArea textarea { border: 2px solid #007BFF !important; }
    small { color: #6c757d; font-size: 0.85em; display: block; }
    th { background-color: #007BFF !important; color: white !important; }
    table { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC & STATE ---
if "history" not in st.session_state: st.session_state.history = []
if "latest_roster" not in st.session_state: st.session_state.latest_roster = ""
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])

# --- 3. SIDEBAR (Reference & History) ---
with st.sidebar:
    st.title("🏥 Control Center")
    with st.expander("👨‍⚕️ Staff Reference", expanded=True):
        st.markdown("**Docs:** Mark, Shawn\n\n**Surgeons:** Axel, Sarah\n\n**Nurses:** Elena, David, Chloe, James, Maya, Leo")
    
    st.divider()
    if st.button("🔄 Clear All History"):
        st.session_state.history = []
        st.rerun()

    st.subheader("📜 Version History")
    for i, version_md in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.markdown(version_md, unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
st.title("Surgery Unit Roster Lab")

c1, c2, c3 = st.columns(3)
with c1: sys_r = st.text_area("🛡️ System Rules", value="- Exactly 1 OFF day per person.", height=150)
with c2: hard_r = st.text_area("🛑 Hard Rules", value="- Mark works Days.", height=150)
with c3: soft_r = st.text_area("✨ Soft Rules", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate New Roster", type="primary", use_container_width=True):
    with st.spinner("AI Generating & Auditing..."):
        st.session_state.latest_roster = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO
        )

# --- 5. THE DRAFT & SAVE MECHANISM ---
if st.session_state.latest_roster:
    st.divider()
    st.subheader("📋 AI Draft Preview")
    
    # Render the AI's output (includes the compliance report)
    st.markdown(st.session_state.latest_roster, unsafe_allow_html=True)

    # Logic to extract the table and save a formatted version
    table_match = re.search(r'(\|.*\|[\s\S]*?\|)', st.session_state.latest_roster)
    
    if table_match:
        if st.button("💾 Save as New Version", type="primary", use_container_width=True):
            try:
                # Parse the raw table to format it
                df = pd.read_html(io.StringIO(table_match.group(1)), flavor='bs4')[0]
                
                # MERGE Name + Designation into the "Clean" multiline format
                df["Name"] = df.apply(lambda x: f"**{x['Name']}**<br><small>{x['Designation']}</small>", axis=1)
                df = df.drop(columns=["Designation"])
                
                # Convert back to Markdown and save to history
                formatted_md = df.to_markdown(index=False)
                st.session_state.history.append(formatted_md)
                st.session_state.latest_roster = "" # Clear draft after saving
                st.success("Version saved to sidebar!")
                st.rerun()
            except:
                st.error("Could not format table. Saving raw version instead.")
                st.session_state.history.append(st.session_state.latest_roster)
                st.rerun()