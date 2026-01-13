import streamlit as st
import pandas as pd
import io
from brain import RosterAgent

# --- 1. CONFIGURABLE SHIFT REPOSITORY (Edit this section later as needed) ---
SHIFT_REPO = {
    "Morning": "07:00 - 15:00",
    "Afternoon": "15:00 - 23:00",
    "Night": "23:00 - 07:00",
    "OFF": "Holiday/Leave"
}
ALLOWED_LABELS = list(SHIFT_REPO.keys())

# --- 2. UI Setup ---
st.set_page_config(page_title="Roster Master", layout="wide")

st.markdown("""
<style>
    .stTextArea textarea { border: 2px solid #007BFF !important; }
    [data-testid="column"] { background-color: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #ddd; }
    /* Style for the Designation below name */
    small { color: #6c757d; font-size: 0.85em; font-weight: 400; }
    th { background-color: #007BFF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. Session State ---
if "history" not in st.session_state: st.session_state.history = []
if "latest_roster" not in st.session_state: st.session_state.latest_roster = ""
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])

# --- 4. Sidebar ---
with st.sidebar:
    st.title("⚙️ Backend Config")
    with st.expander("📝 Current Shift Repository", expanded=True):
        for shift, time in SHIFT_REPO.items():
            st.write(f"**{shift}**: {time}")
    
    st.divider()
    if st.button("🗑️ Reset Memory"):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()

    st.subheader("📚 Version History")
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.markdown(content)

# --- 5. Main UI ---
st.title("🏥 Surgery Unit: Roster Lab")

c1, c2, c3 = st.columns(3)
with c1: sys_r = st.text_area("System Rules", value="- Exactly 1 OFF day per person.", height=150)
with col2 := c2: hard_r = st.text_area("Hard Rules", value="- Mark works Days.", height=150)
with col3 := c3: soft_r = st.text_area("Soft Rules", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate Draft", type="primary", use_container_width=True):
    with st.spinner("AI is calculating and auditing..."):
        # We pass SHIFT_REPO so the AI knows which shifts exist
        res = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO
        )
        st.session_state.latest_roster = res

# --- 6. Editor & Save Mechanism ---
if st.session_state.latest_roster:
    st.divider()
    st.subheader("✏️ Manual Review & Edit")
    
    try:
        # Convert AI markdown to Editable Table
        df_list = pd.read_html(io.StringIO(st.session_state.latest_roster), flavor='bs4')
        if df_list:
            df = df_list[0]
            
            # Use data_editor to allow shift selection from the Repo
            edited_df = st.data_editor(
                df,
                column_config={
                    col: st.column_config.SelectboxColumn(options=ALLOWED_LABELS) 
                    for col in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                },
                hide_index=True,
                use_container_width=True
            )

            if st.button("💾 Save to History"):
                # Append the edited result to history
                final_output = edited_df.to_markdown(index=False)
                st.session_state.history.append(final_output)
                st.success("Version Saved!")
                st.rerun()
                
    except Exception:
        # Fallback if markdown is messy
        st.markdown(st.session_state.latest_roster)