"""
TileGenie - Genie-Powered Production Intelligence App
Entrypoint for Databricks Community Contest: Genie-Powered App Challenge
Track A: Real-World Problem Solver
"""

import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.genie import MessageStatus
import time
import subprocess
import sys

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="TileGenie - Production Intelligence",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for branded styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: #bfdbfe;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Summary metrics */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

# Initialize Databricks client
w = WorkspaceClient()

# Get Genie Space ID from environment (injected by app.yaml)
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")
if not GENIE_SPACE_ID:
    st.error("❌ **Configuration Error:** GENIE_SPACE_ID not found. Ensure the Genie Agent is added as a resource in app.yaml.")
    st.stop()

# Session state initialization
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🟦 TileGenie</h1>
    <p>Ask your factory floor anything.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SUMMARY METRICS STRIP
# ============================================================================

def load_summary_metrics():
    """Load lightweight summary metrics from the database."""
    try:
        # Today's production vs plan
        query = """
        SELECT 
            SUM(actual_units) as total_actual,
            SUM(planned_units) as total_planned,
            ROUND(100.0 * SUM(actual_units) / NULLIF(SUM(planned_units), 0), 1) as efficiency_pct
        FROM tile_production_demo.gold.fact_production_daily
        WHERE production_date = CURRENT_DATE()
        """
        production_df = w.workspace.query_sql(query)
        
        # Active machines (not in breakdown)
        query = """
        WITH latest_status AS (
            SELECT machine_id, status,
                   ROW_NUMBER() OVER (PARTITION BY machine_id ORDER BY start_time DESC) as rn
            FROM tile_production_demo.gold.fact_machine_status_log
        )
        SELECT 
            COUNT(*) as total_machines,
            SUM(CASE WHEN status = 'Running' THEN 1 ELSE 0 END) as running_machines
        FROM latest_status
        WHERE rn = 1
        """
        machine_df = w.workspace.query_sql(query)
        
        # Low stock products
        query = """
        WITH latest_inventory AS (
            SELECT warehouse_id, product_id, stock_quantity, reorder_point,
                   ROW_NUMBER() OVER (PARTITION BY warehouse_id, product_id ORDER BY snapshot_date DESC) as rn
            FROM tile_production_demo.gold.fact_inventory_snapshot
        )
        SELECT COUNT(DISTINCT product_id) as low_stock_count
        FROM latest_inventory
        WHERE rn = 1 AND stock_quantity < reorder_point
        """
        inventory_df = w.workspace.query_sql(query)
        
        return {
            "production": production_df.iloc[0] if not production_df.empty else None,
            "machines": machine_df.iloc[0] if not machine_df.empty else None,
            "inventory": inventory_df.iloc[0] if not inventory_df.empty else None
        }
    except Exception as e:
        return None

with st.spinner("Loading dashboard..."):
    metrics = load_summary_metrics()

if metrics:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if metrics["production"] is not None:
            actual = int(metrics["production"]["total_actual"] or 0)
            planned = int(metrics["production"]["total_planned"] or 0)
            st.metric(
                label="🏭 Today's Production",
                value=f"{actual:,} units",
                delta=f"{actual - planned:+,} vs plan"
            )
        else:
            st.metric("🏭 Today's Production", "No data")
    
    with col2:
        if metrics["production"] is not None:
            efficiency = metrics["production"]["efficiency_pct"] or 0
            st.metric(
                label="🎯 Efficiency",
                value=f"{efficiency}%",
                delta=f"{efficiency - 100:.1f}%"
            )
        else:
            st.metric("🎯 Efficiency", "--")
    
    with col3:
        if metrics["machines"] is not None:
            running = int(metrics["machines"]["running_machines"] or 0)
            total = int(metrics["machines"]["total_machines"] or 0)
            st.metric(
                label="⚙️ Active Machines",
                value=f"{running}/{total}"
            )
        else:
            st.metric("⚙️ Active Machines", "--")
    
    with col4:
        if metrics["inventory"] is not None:
            low_stock = int(metrics["inventory"]["low_stock_count"] or 0)
            st.metric(
                label="⚠️ Low Stock Products",
                value=str(low_stock),
                delta="Needs reorder" if low_stock > 0 else "All adequate"
            )
        else:
            st.metric("⚠️ Low Stock Products", "--")

st.divider()

# ============================================================================
# GENIE CHAT INTERFACE
# ============================================================================

st.subheader("🤖 Ask TileGenie")
st.caption("Ask questions about production, inventory, machines, sales, and forecasts in plain English.")

# Example questions
with st.expander("💡 Example questions you can ask"):
    st.markdown("""
    - Why was production reduced yesterday?
    - What is the expected production for next quarter?
    - How much stock do we have in each warehouse?
    - Which machines had the most downtime this week?
    - What is our defect rate by product type?
    - Show me orders from recent trade shows
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Render structured data if present
        if "dataframe" in message and message["dataframe"] is not None:
            st.dataframe(message["dataframe"], use_container_width=True)
        
        if "chart" in message and message["chart"] is not None:
            st.plotly_chart(message["chart"], use_container_width=True)

# Chat input
if prompt := st.chat_input("Ask a question about your operations..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response from Genie
    with st.chat_message("assistant"):
        with st.spinner("🧪 Analyzing your data..."):
            try:
                # Start or continue conversation
                if st.session_state.conversation_id is None:
                    conversation = w.genie.start_conversation(
                        space_id=GENIE_SPACE_ID
                    )
                    st.session_state.conversation_id = conversation.conversation_id
                
                # Send message to Genie
                message_response = w.genie.create_message(
                    space_id=GENIE_SPACE_ID,
                    conversation_id=st.session_state.conversation_id,
                    content=prompt
                )
                
                # Poll for response
                max_wait = 60  # 60 seconds timeout
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    message = w.genie.get_message(
                        space_id=GENIE_SPACE_ID,
                        conversation_id=st.session_state.conversation_id,
                        message_id=message_response.id
                    )
                    
                    if message.status == MessageStatus.COMPLETED:
                        # Extract response content
                        response_text = ""
                        response_df = None
                        response_chart = None
                        
                        if message.attachments:
                            for attachment in message.attachments:
                                if attachment.text:
                                    response_text += attachment.text.content + "\n"
                                
                                # Check for query results
                                if attachment.query and attachment.query.query_result:
                                    result = attachment.query.query_result
                                    if result.row_count and result.row_count > 0:
                                        # Convert to DataFrame
                                        data = []
                                        if result.data_array:
                                            for row in result.data_array:
                                                data.append(row)
                                        
                                        if data and result.schema and result.schema.columns:
                                            columns = [col.name for col in result.schema.columns]
                                            response_df = pd.DataFrame(data, columns=columns)
                                            
                                            # Create a simple chart if numeric data
                                            numeric_cols = response_df.select_dtypes(include=['number']).columns
                                            if len(numeric_cols) > 0 and len(response_df) <= 20:
                                                # Bar chart for reasonable data sizes
                                                if len(response_df.columns) >= 2:
                                                    x_col = response_df.columns[0]
                                                    y_col = numeric_cols[0]
                                                    response_chart = px.bar(
                                                        response_df.head(15),
                                                        x=x_col,
                                                        y=y_col,
                                                        title=f"{y_col} by {x_col}"
                                                    )
                        
                        # Display response
                        if response_text:
                            st.write(response_text)
                        else:
                            st.write("✅ Query executed successfully.")
                        
                        if response_df is not None:
                            st.dataframe(response_df, use_container_width=True)
                        
                        if response_chart is not None:
                            st.plotly_chart(response_chart, use_container_width=True)
                        
                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text or "✅ Query executed successfully.",
                            "dataframe": response_df,
                            "chart": response_chart
                        })
                        break
                    
                    elif message.status == MessageStatus.FAILED:
                        error_msg = "❌ Sorry, I encountered an error processing your question. Please try rephrasing or ask something else."
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        break
                    
                    time.sleep(1)  # Poll every second
                
                else:
                    # Timeout
                    timeout_msg = "⌛ Query timed out. Your question might be too complex. Try a simpler query."
                    st.warning(timeout_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": timeout_msg
                    })
            
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# ============================================================================
# ADMIN UTILITIES (Sidebar)
# ============================================================================

with st.sidebar:
    st.header("⚙️ Admin Tools")
    
    # Toggle admin panel
    if st.button("🔧 Show/Hide Utilities"):
        st.session_state.show_admin = not st.session_state.show_admin
    
    if st.session_state.show_admin:
        st.divider()
        
        st.subheader("📦 Data Management")
        
        # Generate Data button
        if st.button("🔄 Regenerate Synthetic Data", help="Runs the data generator to refresh all 16 tables"):
            with st.spinner("Generating synthetic data... This may take 2-3 minutes."):
                try:
                    # Run the data generator script
                    script_path = "/Workspace/Users/ashish@lucentinnovation.com/TileGenie/scripts/generate_tile_production_data.py"
                    result = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Data regenerated successfully!")
                        st.code(result.stdout)
                        st.rerun()
                    else:
                        st.error(f"❌ Data generation failed:\n{result.stderr}")
                except subprocess.TimeoutExpired:
                    st.error("❌ Data generation timed out (>5 minutes)")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        st.divider()
        
        # Pull Data button (simulated)
        st.subheader("📥 Data Ingestion")
        if st.button("🔽 Pull Data from Sources", help="Simulates pulling from warehouse/CRM/ERP systems"):
            with st.spinner("Simulating data pull from external sources..."):
                time.sleep(2)  # Simulate processing
                st.info("""
                📡 **Simulated Data Pull Complete**
                
                In production, this would:
                - Connect to warehouse management systems via APIs
                - Pull CRM data from Salesforce/HubSpot
                - Extract ERP data from SAP/Oracle
                - Stage data in bronze tables
                - Run transformation pipelines to gold layer
                
                For this demo, we're using synthetic generated data.
                """)
        
        st.divider()
        
        st.subheader("📊 App Info")
        st.markdown(f"""
        **Genie Space ID:**  
        `{GENIE_SPACE_ID[:20]}...`
        
        **Tables:** 16  
        **Catalog:** tile_production_demo  
        **Schema:** gold
        """)
        
        if st.button("🔄 Clear Chat History"):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("""
🏆 **TileGenie** | Built for Databricks Community Contest: Genie-Powered App Challenge  
Track A: Real-World Problem Solver | Powered by Genie Agent
""")