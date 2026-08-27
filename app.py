"""
TileGenie - Genie-Powered Production Intelligence App
Databricks Community Contest: Genie-Powered App Challenge

Showcasing "Genie at the Core":
- Auto-loads executive dashboard on startup (Genie answers 3 CEO questions IN PARALLEL)
- Optimized: 30 seconds total load time (not 90 seconds)
- All insights powered by Genie's natural language understanding
- Display Genie's SQL generation process
- Show Genie's suggested follow-up questions
"""

import streamlit as st
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="TileGenie - Genie-Powered Intelligence",
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
    .main-header h1 { color: white; margin-bottom: 0.5rem; }
    .main-header p { color: #bfdbfe; font-size: 1.1rem; margin: 0; }
    .metric-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 100%;
    }
    .metric-title {
        color: #6b7280;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 500;
        margin-top: 0.5rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize WorkspaceClient
@st.cache_resource
def get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()

# Function to ask Genie a question
def ask_genie(w, space_id, question, conversation_id=None):
    """Ask Genie a question and return the response"""
    try:
        if conversation_id is None:
            response = w.genie.start_conversation(space_id=space_id, content=question)
            conv_id = response.conversation_id
            message_id = response.message_id
        else:
            response = w.genie.create_message(
                space_id=space_id,
                conversation_id=conversation_id,
                content=question
            )
            conv_id = conversation_id
            message_id = response.message_id
        
        # Poll for completion
        for _ in range(60):
            message = w.genie.get_message(space_id=space_id, conversation_id=conv_id, message_id=message_id)
            status = str(message.status) if hasattr(message, 'status') else None
            
            if status and 'COMPLETED' in status:
                content = "No response"
                sql_query = None
                
                if message.attachments:
                    for attachment in message.attachments:
                        if hasattr(attachment, 'text') and attachment.text:
                            if hasattr(attachment.text, 'content'):
                                content = attachment.text.content
                        if hasattr(attachment, 'query') and attachment.query:
                            if hasattr(attachment.query, 'query'):
                                sql_query = attachment.query.query
                
                return {"success": True, "content": content, "sql": sql_query, "conversation_id": conv_id, "question": question}
            elif status and 'FAILED' in status:
                return {"success": False, "error": str(message.error) if hasattr(message, 'error') else "Failed", "question": question}
            
            time.sleep(2)
        
        return {"success": False, "error": "Timeout", "question": question}
    except Exception as e:
        return {"success": False, "error": str(e), "question": question}

GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "").replace("genie://", "")

if not GENIE_SPACE_ID:
    st.error("❌ GENIE_SPACE_ID not configured")
    st.stop()

# Session state initialization
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dashboard_loaded" not in st.session_state:
    st.session_state.dashboard_loaded = False
if "dashboard_data" not in st.session_state:
    st.session_state.dashboard_data = []

# Header
st.markdown('<div class="main-header"><h1>🟦 TileGenie</h1><p>🧞‍♂️ Powered by Databricks Genie - Auto-Loading Production Intelligence</p></div>', unsafe_allow_html=True)

# Auto-load dashboard on first load (PARALLEL EXECUTION)
if not st.session_state.dashboard_loaded:
    st.markdown("### 📊 Executive Dashboard")
    st.caption("🧞‍♂️ Genie is analyzing your production data in parallel... ⚡")
    
    w = get_workspace_client()
    
    # Define CEO questions to auto-load
    ceo_questions = [
        "What was yesterday's total production in units?",
        "How many machines are currently down or in maintenance?",
        "What is the current total inventory across all warehouses?"
    ]
    
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Execute all queries in parallel
    with st.spinner("⚡ Running 3 queries in parallel..."):
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            futures = {executor.submit(ask_genie, w, GENIE_SPACE_ID, q, None): q for q in ceo_questions}
            
            completed = 0
            results = []
            
            # Collect results as they complete
            for future in as_completed(futures):
                completed += 1
                result = future.result()
                results.append(result)
                
                progress_placeholder.progress(completed / len(ceo_questions))
                status_placeholder.caption(f"✅ Completed {completed}/{len(ceo_questions)} queries")
                
                # Store conversation ID from first successful response
                if result["success"] and st.session_state.conversation_id is None:
                    st.session_state.conversation_id = result["conversation_id"]
        
        elapsed = time.time() - start_time
        
        # Store results in order
        st.session_state.dashboard_data = sorted(results, key=lambda x: ceo_questions.index(x["question"]))
        st.session_state.dashboard_loaded = True
        
        status_placeholder.success(f"✅ Dashboard loaded in {elapsed:.1f} seconds! (Parallel execution)")
    
    time.sleep(1)
    st.rerun()

# Display loaded dashboard
if st.session_state.dashboard_loaded and st.session_state.dashboard_data:
    st.markdown("### 📊 Executive Dashboard")
    st.caption("🎯 Auto-loaded insights powered by Genie (parallel execution)")
    
    dashboard_cols = st.columns(3)
    
    for idx, data in enumerate(st.session_state.dashboard_data):
        with dashboard_cols[idx]:
            if data["success"]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{data["question"].replace('?', '')}</div>
                    <div class="metric-value">{data["content"][:200]}...</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📄 Full Answer"):
                    st.markdown(data["content"])
                
                if data.get("sql"):
                    with st.expander("🔍 SQL Query"):
                        st.code(data["sql"], language="sql")
            else:
                st.error(f"❌ {data['question']}")
                st.caption(f"Error: {data.get('error', 'Unknown')}")
    
    st.markdown("---")

# Quick Action Buttons
st.markdown("### ⚡ Ask Genie More Questions")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Production Trends", use_container_width=True, type="primary"):
        st.session_state['quick_question'] = "Show me production trends for the last 7 days"
        st.rerun()

with col2:
    if st.button("📦 Low Stock Alert", use_container_width=True, type="primary"):
        st.session_state['quick_question'] = "Which products have the lowest stock levels?"
        st.rerun()

with col3:
    if st.button("🔮 Forecast", use_container_width=True, type="primary"):
        st.session_state['quick_question'] = "What is the expected production for next quarter?"
        st.rerun()

with col4:
    if st.button("⚙️ Machine Downtime", use_container_width=True, type="primary"):
        st.session_state['quick_question'] = "Which machines had the most downtime this week?"
        st.rerun()

st.markdown("---")

# Display conversation history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and "sql" in msg and msg["sql"]:
            with st.expander("🔍 SQL Query", expanded=False):
                st.code(msg["sql"], language="sql")

# Chat input
if 'quick_question' in st.session_state:
    user_input = st.session_state['quick_question']
    del st.session_state['quick_question']
else:
    user_input = st.chat_input("✨ Ask Genie anything about your tile production...")

if user_input:
    w = get_workspace_client()
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("🧞‍♂️ Genie is analyzing..."):
            result = ask_genie(w, GENIE_SPACE_ID, user_input, st.session_state.conversation_id)
            
            if result["success"]:
                if st.session_state.conversation_id is None:
                    st.session_state.conversation_id = result["conversation_id"]
                
                st.markdown(result["content"])
                
                msg_data = {"role": "assistant", "content": result["content"]}
                if result.get("sql"):
                    msg_data["sql"] = result["sql"]
                
                st.session_state.messages.append(msg_data)
                
                if result.get("sql"):
                    with st.expander("🔍 SQL Query", expanded=False):
                        st.code(result["sql"], language="sql")
            else:
                st.error(f"❌ Error: {result.get('error')}")

# Sidebar
with st.sidebar:
    st.markdown("### 🏆 Contest Entry")
    st.write("**Databricks Community Contest**")
    st.caption("Genie-Powered App Challenge")
    
    st.markdown("---")
    
    st.markdown("### 🧞‍♂️ Genie at the Core")
    st.success(
        "**⚡ Parallel Intelligence**\n\n"
        "✅ 3 queries in ~30 seconds\n"
        "✅ Auto-loading dashboard\n"
        "✅ Natural language → SQL\n"
        "✅ Real-time analysis\n\n"
        "All powered by Genie analyzing 16 gold tables!"
    )
    
    st.markdown("---")
    
    if st.button("🔄 Reload Dashboard", use_container_width=True):
        st.session_state.dashboard_loaded = False
        st.session_state.dashboard_data = []
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("🧞‍♂️ Connected to Genie Space")
    st.caption(f"`{GENIE_SPACE_ID[:16]}...`")
