"""
TileGenie - Genie-Powered Production Intelligence App
Databricks Community Contest: Genie-Powered App Challenge

Features:
- Natural language chat with Genie AI
- CEO dashboard with key metrics
- Quick action buttons for common questions
- Visualization support
- Suggested questions
"""

import streamlit as st
import os
import time
import pandas as pd

st.set_page_config(
    page_title="TileGenie",
    page_icon="🟦",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 { color: white; }
</style>
""", unsafe_allow_html=True)

# Initialize WorkspaceClient inside a cached function
@st.cache_resource
def get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()

GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "").replace("genie://", "")

if not GENIE_SPACE_ID:
    st.error("❌ GENIE_SPACE_ID not configured")
    st.stop()

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="main-header"><h1>🟦 TileGenie</h1><p style="color: #bfdbfe">Ask your factory floor anything</p></div>', unsafe_allow_html=True)

st.write("### Try these questions:")
st.write("- Why was production reduced yesterday?")
st.write("- What is the expected production of Porcelain-Glossy-24x24 for next quarter?")
st.write("- How much stock do we have in each warehouse?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask about production, inventory, machines..."):
    w = get_workspace_client()
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if not st.session_state.conversation_id:
                    response = w.genie.start_conversation(space_id=GENIE_SPACE_ID, content=user_input)
                    st.session_state.conversation_id = response.conversation_id
                    message_id = response.message_id
                else:
                    response = w.genie.create_message(
                        space_id=GENIE_SPACE_ID,
                        conversation_id=st.session_state.conversation_id,
                        content=user_input
                    )
                    message_id = response.message_id
                
                for _ in range(60):
                    message = w.genie.get_message(space_id=GENIE_SPACE_ID, conversation_id=st.session_state.conversation_id, message_id=message_id)
                    
                    # Check status as string (no enum import needed)
                    status = str(message.status) if hasattr(message, 'status') else None
                    
                    if status and 'COMPLETED' in status:
                        # Extract the text answer from attachments
                        content = "No response"
                        
                        if message.attachments:
                            # Look for the text attachment (usually attachments[1])
                            for attachment in message.attachments:
                                if hasattr(attachment, 'text') and attachment.text:
                                    if hasattr(attachment.text, 'content'):
                                        content = attachment.text.content
                                        break
                        
                        st.markdown(content)
                        st.session_state.messages.append({"role": "assistant", "content": content})
                        break
                    elif status and 'FAILED' in status:
                        error_msg = f"Genie failed to process the message.\n\nStatus: {status}"
                        if hasattr(message, 'error'):
                            error_msg += f"\n\nError: {message.error}"
                        st.error(error_msg)
                        st.write("Debug info:")
                        st.write(f"- Space ID: {GENIE_SPACE_ID}")
                        st.write(f"- Conversation ID: {st.session_state.conversation_id}")
                        st.write(f"- Message ID: {message_id}")
                        break
                    
                    time.sleep(2)
            except Exception as e:
                st.error(f"Error calling Genie API: {str(e)}")
                st.write(f"Error type: {type(e).__name__}")
                import traceback
                st.code(traceback.format_exc())

with st.sidebar:
    st.markdown("### 🏆 Contest Entry")
    st.write("Databricks Community Contest")
    if st.button("Reset Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
