# MUST BE AT THE VERY TOP for Streamlit Cloud
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import streamlit as st
import brain

st.set_page_config(page_title="Perk AI | Expert Mode", layout="wide")

# Initialize the RAG Agent
if "agent" not in st.session_state:
    st.session_state.agent = brain.PerkAgent(st.secrets["GEMINI_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR: KNOWLEDGE & CONTROLS ---
with st.sidebar:
    st.title("📂 Knowledge Base")
    file = st.file_uploader("Upload Policy (.txt)", type="txt")
    if file and st.button("Index Documents", use_container_width=True):
        with st.status("Embedding...", expanded=False):
            count = st.session_state.agent.add_documents(file.getvalue().decode("utf-8"))
        st.success(f"Indexed {count} lines!")

    st.divider()
    
    st.header("⚙️ Model Tuning")
    sys_p = st.text_area("System Prompt", 
                         value="Be a context reportee. Use information given only in context to address user query.",
                         height=100)
    
    col1, col2 = st.columns(2)
    with col1:
        temp = st.slider("Temperature", 0.0, 1.0, 0.2)
        top_p = st.slider("Top P", 0.0, 1.0, 0.9)
    with col2:
        max_t = st.number_input("Max Tokens", 10, 2000, 500)
        stop_s = st.text_input("Stop Seq (csv)", placeholder="e.g. END")

    # Bundle settings for the agent
    ui_settings = {
        "system_prompt": sys_p,
        "temperature": temp,
        "top_p": top_p,
        "max_tokens": max_t,
        "sequences": stop_s
    }

# --- MAIN CHAT ---
st.title("Your Custom AI")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about the policy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Thinking...") as status:
            # Pass BOTH the prompt and the UI settings
            response = st.session_state.agent.ask(prompt, ui_settings)
            status.update(label="Complete", state="complete")
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})