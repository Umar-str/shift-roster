import streamlit as st
import brain

st.set_page_config(layout="wide", page_title="Hospital Roster Lab")

# Initialize Agent
if "roster_agent" not in st.session_state:
    st.session_state.roster_agent = brain.RosterAgent(st.secrets["GEMINI_API_KEY"])

st.title("🏥 10-Employee Hospital Roster Generator")
st.markdown("Edit the rules below to test the AI's scheduling logic.")

# --- THREE COLUMN RULE INTERFACE ---
c1, c2, c3 = st.columns(3)

with c1:
    st.info("🛡️ System Rules")
    sys_rules = st.text_area("Fixed constraints:", 
        value="- Max 1 shift per 24 hours.\n- Min 11 hours rest between shifts.\n- No person works more than 6 days in a row.",
        height=200)

with c2:
    st.error("🛑 Hard Rules")
    hard_rules = st.text_area("Mandatory user rules:", 
        value="- Surgery requires: 1 Surgeon, 1 Anesthes., 2 Nurses.\n- Mark (Doctor) must work all Day shifts.\n- Axel (Surgeon) is OFF Wednesday.",
        height=200)

with c3:
    st.success("✨ Soft Rules")
    soft_rules = st.text_area("User preferences:", 
        value="- Prefer Morning shifts for Elena.\n- Try to pair James and Chloe on the same shifts.",
        height=200)

# --- EXECUTION ---
if st.button("Generate Roster", use_container_width=True, type="primary"):
    with st.spinner("AI is calculating the most efficient schedule..."):
        result = st.session_state.roster_agent.generate_roster(sys_rules, hard_rules, soft_rules)
        
        st.divider()
        st.subheader("🗓️ Generated 7-Day Schedule")
        st.markdown(result)

# --- DEBUG / SIDEBAR ---
with st.sidebar:
    st.header("Staff List")
    st.write("1. Mark (Doctor)\n2. Shawn (Anesthes)\n3. Axel (Surgeon)\n4. Sarah (Surgeon)\n5. Elena (Nurse)\n6. David (Nurse)\n7. Chloe (Nurse)\n8. James (Nurse)\n9. Maya (Nurse)\n10. Leo (Nurse)")