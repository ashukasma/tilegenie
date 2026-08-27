"""
TileGenie - Genie-Powered Production Intelligence App
Databricks Community Contest: Genie-Powered App Challenge
FIXED VERSION - Proper authentication for Databricks Apps
"""

import streamlit as st
import os
import time

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

# Initialize WorkspaceClient INSIDE a function, not at module level
@st.cache_resource
def get_workspace_client():
    """Initialize WorkspaceClient with proper app authentication"""
    from databricks.sdk import WorkspaceClient
    try:
        # In Databricks Apps, WorkspaceClient() should automatically use
        # the app's service principal credentials
        return WorkspaceClient()
    except Exception as e:
        st.error(f"Failed to initialize Databricks client: {e}")
        return None

# Get Genie Space ID from environment
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "").replace("genie://", "")

if not GENIE_SPACE_ID:
    st.error("❌ GENIE_SPACE_ID not configured in app.yaml")
    st.stop()

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# UI Header
st.markdown('<div class="main-header"><h1>🟦 TileGenie</h1><p style="color: #bfdbfe">Ask your factory floor anything</p></div>', unsafe_allow_html=True)

# Sample questions
st.write("### Try these questions:")
st.write("- Why was production reduced yesterday?")
st.write("- What is the expected production of Porcelain-Glossy-24x24 for next quarter?")
st.write("- How much stock do we have in each warehouse?")

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask about production, inventory, machines..."):
    # Get WorkspaceClient (will be cached)
    w = get_workspace_client()
    
    if not w:
        st.error("❌ Could not initialize Databricks client")
        st.stop()
    
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get response from Genie
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from databricks.sdk.service.genie import MessageStatus
                
                # Start or continue conversation
                if not st.session_state.conversation_id:
                    response = w.genie.start_conversation(
                        space_id=GENIE_SPACE_ID,
                        content=user_input
                    )
                    st.session_state.conversation_id = response.conversation_id
                    message_id = response.message_id
                else:
                    response = w.genie.create_message(
                        space_id=GENIE_SPACE_ID,
                        conversation_id=st.session_state.conversation_id,
                        content=user_input
                    )
                    message_id = response.id
                
                # Poll for response
                for attempt in range(60):
                    message = w.genie.get_message(
                        space_id=GENIE_SPACE_ID,
                        conversation_id=st.session_state.conversation_id,
                        message_id=message_id
                    )
                    
                    if message.status == MessageStatus.COMPLETED:
                        content = message.attachments[0].text.content if message.attachments else "No response"
                        st.markdown(content)
                        st.session_state.messages.append({"role": "assistant", "content": content})
                        break
                    elif message.status == MessageStatus.FAILED:
                        error_msg = "Genie failed to process the message"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        break
                    
                    time.sleep(2)
                else:
                    timeout_msg = "Response timed out after 2 minutes"
                    st.error(timeout_msg)
                    st.session_state.messages.append({"role": "assistant", "content": timeout_msg})
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar
with st.sidebar:
    st.markdown("### 🏆 Contest Entry")
    st.write("Databricks Community Contest")
    st.write("Genie-Powered App Challenge")
    st.write("---")
    st.write(f"**Genie Space:** {GENIE_SPACE_ID[:8]}...")
    
    if st.button("Reset Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
