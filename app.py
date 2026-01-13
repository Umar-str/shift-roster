import streamlit as st
import pandas as pd
import io
import re
from brain import RosterAgent

# --- 1. CONFIG ---
SHIFT_REPO = ["Morning", "Evening", "Night", "OFF"]

st.set_page_config(page_title="Roster Master", layout="wide")

st.markdown("""
<style>
    .stTextArea textarea { border: 2px solid #007BFF !important; border-radius: 8px; }
    [data-testid="column"] { background-color: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #dee2e6; }
    th { background-color: #007BFF !important; color: white !important; }
    small { color: #6c757d; font-size: 0.85em; display: block; line-height: 1.2; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGIC ---
if "history" not in st.session_state: st.session_state.history = []
if "latest_roster" not in st.session_state: st.session_state.latest_roster = ""
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = RosterAgent(st.secrets["GEMINI_API_KEY"])

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🏥 Roster Hub")
    with st.expander("👨‍⚕️ Staff Reference", expanded=True):
        st.markdown("- **Mark** (Doc)\n- **Shawn** (Anesth)\n- **Axel/Sarah** (Surg)\n- **Nurses**: Elena, David, Chloe, James, Maya, Leo")
    
    st.divider()
    if st.button("🔄 Reset Memory"):
        st.session_state.history = []
        st.session_state.latest_roster = ""
        st.rerun()

    st.subheader("📜 History")
    for i, content in enumerate(reversed(st.session_state.history)):
        with st.expander(f"Version {len(st.session_state.history)-i}"):
            st.markdown(content, unsafe_allow_html=True)

# --- 4. INPUTS ---
st.title("Surgery Unit: Roster Lab")
c1, c2, c3 = st.columns(3)
with c1: sys_r = st.text_area("🛡️ System Rules", value="- Exactly 1 OFF day per person.", height=150)
with c2: hard_r = st.text_area("🛑 Hard Rules", value="- Mark works Day shifts.", height=150)
with c3: soft_r = st.text_area("✨ Soft Rules", value="- Elena prefers Morning.", height=150)

if st.button("🚀 Generate Draft", type="primary", use_container_width=True):
    with st.spinner("AI Audit in progress..."):
        res = st.session_state.roster_agent.generate_roster(sys_r, hard_r, soft_r, st.session_state.history, SHIFT_REPO)
        st.session_state.latest_roster = res

# --- 5. EDITOR & FORMATTER ---
if st.session_state.latest_roster:
    st.divider()
    
    # Extract just the table from the AI response (ignores the compliance report for editing)
    table_match = re.search(r'(\|.*\|[\s\S]*?\|)', st.session_state.latest_roster)
    
    if table_match:
        st.subheader("✏️ Manual Edit Mode")
        table_md = table_match.group(1)
        
        try:
            df = pd.read_html(io.StringIO(table_md), flavor='bs4')[0]
            
            # This grid will now show dropdowns correctly
            edited_df = st.data_editor(
                df,
                column_config={
                    col: st.column_config.SelectboxColumn(options=SHIFT_REPO) 
                    for col in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                },
                hide_index=True, use_container_width=True
            )

            if st.button("💾 Save & Format to History", type="primary"):
                # COMBINE NAME AND ROLE FOR DISPLAY
                final_df = edited_df.copy()
                final_df["Name"] = final_df.apply(lambda x: f"**{x['Name']}** <br><small>{x['Designation']}</small>", axis=1)
                final_df = final_df.drop(columns=["Designation"])
                
                final_md = final_df.to_markdown(index=False)
                st.session_state.history.append(final_md)
                st.session_state.latest_roster = "" # Clear view to show success
                st.success("Committed to Session History!")
                st.rerun()
                
        except Exception:
            st.warning("Table format complexity high. Showing raw preview:")
            st.markdown(st.session_state.latest_roster, unsafe_allow_html=True)
    else:
        st.markdown(st.session_state.latest_roster, unsafe_allow_html=True)
