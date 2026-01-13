import streamlit as st
import pandas as pd
import io
from brain import RosterAgent

# --- 1. SHIFT REPOSITORY (Backend Configuration) ---
# Edit these labels whenever you need to change the shift types
SHIFT_REPO = ["Morning", "Evening", "Night", "OFF"]

# --- 2. Page Config & Professional UI ---
st.set_page_config(page_title="Roster Lab", layout="wide")

st.markdown("""
<style>
    /* Distinguished Blue Borders */
    .stTextArea textarea { border: 2px solid #007BFF !important; border-radius: 8px; }
    
    /* Rules Containers */
    [data-testid="column"] { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 12px; 
        border: 1px solid #dee2e6; 
    }
    
    /* Table Styling for Small Designation */
    small { color: #6c757d; font-size: 0.85em; display: block; line-height: 1.2; }
    th { background-color: #007BFF !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. Session Initialization ---
if "history" not in st.session_state: st.session_state.history = []
if "latest_roster" not in st.session_state: st.session_state.latest_roster = ""
if "roster_agent" not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Missing API Key in Secrets.")

# --- 4. Sidebar: Staff Reference, History & Reset ---
with st.sidebar:
    st.title("🏥 Roster Controls")
    
    # NEW: Reference Staff List
    with st.expander("👨‍⚕️ Staff Reference", expanded=True):
        st.markdown("""
        **Doctors/Anesthesiology**
        - Mark (Doc)
        - Shawn (Anesth)
        
        **Surgeons**
        - Axel
        - Sarah
        
        **Nurses**
        - Elena, David, Chloe, 
        - James, Maya, Leo
        """)

    with st.expander("📝 Shift Repository"):
        st.code(SHIFT_REPO)
    
    st.divider()
    if st.button("🔄 Reset Memory", use_container_width=True):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()

    st.subheader("📜 Version History")
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.text_area("Copyable content", value=content, height=200, key=f"hist_{i}")

# --- 5. Main Inputs Area ---
st.title("Surgery Unit Roster Lab")

col1, col2, col3 = st.columns(3)
with col1:
    sys_r = st.text_area("🛡️ System Rules", value="- Exactly 1 OFF day per person.", height=150)
with col2:
    hard_r = st.text_area("🛑 Hard Rules", value="- Mark works Day shifts.", height=150)
with col3:
    soft_r = st.text_area("✨ Soft Rules", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate Draft with AI", type="primary", use_container_width=True):
    with st.spinner("AI calculating shifts..."):
        res = st.session_state.roster_agent.generate_roster(
            sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO
        )
        st.session_state.latest_roster = res

# --- 6. The Editor & Versioning ---
if st.session_state.latest_roster:
    st.divider()
    st.subheader("✏️ Interactive Roster Editor")
    st.caption("Click any cell to change the shift via dropdown.")
    
    try:
        # Convert AI markdown to a Pandas Dataframe
        df = pd.read_html(io.StringIO(st.session_state.latest_roster), flavor='bs4')[0]
        
        # Grid Editor with Dropdowns from Repository
        edited_df = st.data_editor(
            df,
            column_config={
                col: st.column_config.SelectboxColumn(options=SHIFT_REPO) 
                for col in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            },
            hide_index=True, 
            use_container_width=True
        )

        if st.button("💾 Save Changes & Commit to History", type="primary"):
            final_md = edited_df.to_markdown(index=False)
            st.session_state.history.append(final_md)
            st.success("Version saved!")
            st.rerun()

    except Exception:
        st.markdown(st.session_state.latest_roster)