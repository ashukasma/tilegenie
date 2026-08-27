# TileGenie Architecture Documentation
**Genie-Powered Production Intelligence App**

## Executive Summary

TileGenie is a Genie-powered AI application that provides auto-loading production intelligence for tile manufacturing operations. It leverages Databricks Genie to translate natural language questions into SQL queries against 16 gold tables, providing instant insights for executives, operations managers, and data analysts.

**Key Innovation:** Parallel query execution reduces dashboard load time from 90s to 30s, showcasing real-time AI intelligence.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TileGenie App (Streamlit)                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     User Interface Layer                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │ │
│  │  │ Auto-Loading │  │ Quick Action │  │     Chat     │        │ │
│  │  │  Dashboard   │  │   Buttons    │  │  Interface   │        │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  Application Logic Layer                        │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Parallel Query Executor (ThreadPoolExecutor)            │ │ │
│  │  │  - Submits 3 CEO questions simultaneously                │ │ │
│  │  │  - Collects results as they complete                     │ │ │
│  │  │  - Progress tracking & error handling                    │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  ask_genie() Function                                    │ │ │
│  │  │  - Sends natural language question to Genie              │ │ │
│  │  │  - Polls for completion (max 2 minutes)                  │ │ │
│  │  │  - Extracts text, SQL, visualizations from attachments   │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   SDK Integration Layer                         │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Cached WorkspaceClient (@st.cache_resource)            │ │ │
│  │  │  - Single reusable client instance                       │ │ │
│  │  │  - Databricks SDK >= 0.33.0                              │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ Genie API
┌─────────────────────────────────────────────────────────────────────┐
│                    Databricks Genie Service                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Genie Space: TileGenie Production Intelligence               │ │
│  │  ID: 01f1a166e5891c2d89a0256412e7d452                         │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Natural Language Processing                             │ │ │
│  │  │  - Understands user question intent                      │ │ │
│  │  │  - Maps to relevant tables/columns                       │ │ │
│  │  │  - Identifies required joins & filters                   │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  SQL Generation Engine                                   │ │ │
│  │  │  - Generates optimized SQL queries                       │ │ │
│  │  │  - Validates against schema                              │ │ │
│  │  │  - Applies business logic rules                          │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                  │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │  Query Execution & Result Formatting                     │ │ │
│  │  │  - Executes SQL on SQL Warehouse                         │ │ │
│  │  │  - Formats results as text, tables, charts               │ │ │
│  │  │  - Generates suggested follow-up questions               │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ SQL Queries
┌─────────────────────────────────────────────────────────────────────┐
│              Unity Catalog: tile_production_demo.gold                │
│                                                                       │
│  Dimension Tables (7):               Fact Tables (8):                │
│  • dim_customer                      • fact_production_daily         │
│  • dim_event                         • fact_orders                   │
│  • dim_factory                       • fact_inventory_snapshot       │
│  • dim_machine                       • fact_machine_status_log       │
│  • dim_product                       • fact_machine_sensor_reading   │
│  • dim_sales_rep                     • fact_stock_transfer           │
│  • dim_warehouse                     • fact_crm_interaction          │
│                                      • fact_event_attendance         │
│  Analytical Tables (1):                                              │
│  • production_forecast                                               │
│                                                                       │
│  Coverage: 3 factories, 5 warehouses, 180 days operational data     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Layer (Streamlit UI)

```python
# User Interface Components

1. Header
   ├── Gradient banner with TileGenie branding
   └── "Powered by Databricks Genie" messaging

2. Auto-Loading Dashboard (⚡ Key Feature)
   ├── Progress indicator during parallel query execution
   ├── Three metric cards (CEO insights)
   │   ├── Yesterday's Total Production
   │   ├── Machines Down/Maintenance
   │   └── Current Total Inventory
   └── Expandable SQL queries for each metric

3. Quick Action Buttons
   ├── Production Trends (7-day analysis)
   ├── Low Stock Alert (inventory warnings)
   ├── Forecast (next quarter predictions)
   └── Machine Downtime (maintenance tracking)

4. Chat Interface
   ├── Message history display
   ├── User input field
   ├── Assistant responses with SQL visibility
   └── Suggested follow-up questions (future enhancement)

5. Sidebar
   ├── Contest entry information
   ├── "Genie at the Core" messaging
   ├── Reload Dashboard button
   └── Genie Space ID display
```

### 2.2 Application Logic Layer

```python
# Core Business Logic

@st.cache_resource
def get_workspace_client():
    """
    Initialize and cache WorkspaceClient
    - Single instance shared across all requests
    - Avoids repeated authentication overhead
    """
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()

def ask_genie(w, space_id, question, conversation_id=None):
    """
    Core function to interact with Genie API
    
    Parameters:
    - w: WorkspaceClient instance
    - space_id: Genie Space ID (01f1a166e5891c2d89a0256412e7d452)
    - question: Natural language question
    - conversation_id: Optional, for multi-turn conversations
    
    Returns:
    - success: Boolean
    - content: Text answer
    - sql: Generated SQL query
    - conversation_id: For follow-up questions
    
    Flow:
    1. Start conversation or create message
    2. Poll for completion (60 iterations × 2s = 120s max)
    3. Extract content from ALL attachments (critical!)
    4. Return structured response
    """
    
# Parallel Execution Engine
with ThreadPoolExecutor(max_workers=3) as executor:
    """
    Execute multiple Genie queries simultaneously
    - Reduces total time from 90s → 30s
    - Progress tracking for user feedback
    - Error handling per query
    """
```

### 2.3 Data Flow Architecture

```
User Action → App Logic → Genie API → Unity Catalog → Response

Detailed Flow:

1. USER INITIATES REQUEST
   ├── Auto-load on first visit (3 CEO questions)
   ├── Click quick action button
   └── Type in chat input

2. APP PROCESSES REQUEST
   ├── Retrieve cached WorkspaceClient
   ├── Call ask_genie() with question
   └── Display spinner/progress indicator

3. GENIE API INTERACTION
   ├── w.genie.start_conversation() or create_message()
   ├── Poll w.genie.get_message() every 2 seconds
   ├── Check status: RUNNING → COMPLETED/FAILED
   └── Extract from message.attachments[]

4. ATTACHMENT PROCESSING (Critical!)
   ├── Iterate ALL attachments (not just first)
   ├── attachment.text.content → Text answer
   ├── attachment.query.query → SQL query
   ├── attachment.viz → Visualizations (future)
   └── attachment.suggestions → Follow-ups (future)

5. RESPONSE RENDERING
   ├── Display text answer
   ├── Show expandable SQL query
   ├── Update conversation state
   └── Enable follow-up questions
```

---

## 3. Data Architecture

### 3.1 Genie Space Configuration

```yaml
Space Name: TileGenie Production Intelligence
Space ID: 01f1a166e5891c2d89a0256412e7d452
Description: AI-powered production intelligence for tile manufacturing

Tables (16):
  Dimensions:
    - tile_production_demo.gold.dim_customer
    - tile_production_demo.gold.dim_event
    - tile_production_demo.gold.dim_factory
    - tile_production_demo.gold.dim_machine
    - tile_production_demo.gold.dim_product
    - tile_production_demo.gold.dim_sales_rep
    - tile_production_demo.gold.dim_warehouse
  
  Facts:
    - tile_production_demo.gold.fact_crm_interaction
    - tile_production_demo.gold.fact_event_attendance
    - tile_production_demo.gold.fact_inventory_snapshot
    - tile_production_demo.gold.fact_machine_sensor_reading
    - tile_production_demo.gold.fact_machine_status_log
    - tile_production_demo.gold.fact_orders
    - tile_production_demo.gold.fact_production_daily
    - tile_production_demo.gold.fact_stock_transfer
  
  Analytics:
    - tile_production_demo.gold.production_forecast

Data Coverage:
  - 3 Factories (production facilities)
  - 5 Warehouses (inventory locations)
  - 180 Days of operational data
```

### 3.2 Entity Relationships

```
┌─────────────────┐
│  dim_factory    │───┐
└─────────────────┘   │
                      │
┌─────────────────┐   │     ┌─────────────────────────┐
│  dim_machine    │───┼────→│ fact_production_daily   │
└─────────────────┘   │     └─────────────────────────┘
                      │              ↓
┌─────────────────┐   │     ┌─────────────────────────┐
│  dim_product    │───┴────→│   fact_orders           │
└─────────────────┘         └─────────────────────────┘
                                     ↓
┌─────────────────┐         ┌─────────────────────────┐
│ dim_warehouse   │────────→│ fact_inventory_snapshot │
└─────────────────┘         └─────────────────────────┘
                                     ↓
┌─────────────────┐         ┌─────────────────────────┐
│ dim_customer    │────────→│  fact_crm_interaction   │
└─────────────────┘         └─────────────────────────┘

Genie automatically understands these relationships!
```

---

## 4. Technology Stack

### 4.1 Core Technologies

```yaml
Frontend Framework:
  - Streamlit 1.38.0
  - HTML/CSS for custom styling
  - Markdown for rich text formatting

Backend/SDK:
  - databricks-sdk >= 0.33.0 (Genie API support)
  - Python 3.10+
  - concurrent.futures (ThreadPoolExecutor for parallel execution)

Databricks Platform:
  - Databricks Apps (Serverless deployment)
  - Genie Service (NLP + SQL generation)
  - Unity Catalog (Data governance)
  - SQL Warehouse (Query execution)

Data Layer:
  - Delta Lake tables (ACID transactions)
  - Unity Catalog governance (tile_production_demo.gold)
  - Star schema design (dimensions + facts)
```

### 4.2 Dependencies

```txt
# requirements.txt
databricks-sdk>=0.33.0   # Genie SDK support
streamlit~=1.38.0        # Web framework
```

### 4.3 Configuration

```yaml
# app.yaml
command: ["streamlit", "run", "app.py", "--server.port=8080"]

resources:
  - name: genie-space
    genie_space:
      space_id: 01f1a166e5891c2d89a0256412e7d452

env:
  - name: GENIE_SPACE_ID
    value: genie://01f1a166e5891c2d89a0256412e7d452
```

---

## 5. Deployment Architecture

### 5.1 Databricks Apps Platform

```
┌─────────────────────────────────────────────────────────────────┐
│                    Databricks Workspace                          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  App: tile-genie                                           │ │
│  │  ID: 1d333e6f-1345-4e0c-8483-ed88a30b6d0d                 │ │
│  │                                                              │ │
│  │  Compute:                                                    │ │
│  │  ├── Size: MEDIUM                                           │ │
│  │  ├── State: ACTIVE                                          │ │
│  │  └── Serverless (no cluster management)                     │ │
│  │                                                              │ │
│  │  Source:                                                     │ │
│  │  ├── Type: Workspace files                                  │ │
│  │  └── Path: /Workspace/Users/ashish@.../TileGenie           │ │
│  │                                                              │ │
│  │  Service Principal:                                          │ │
│  │  ├── ID: 73721084961770                                     │ │
│  │  ├── Name: app-3nzv6y tile-genie                           │ │
│  │  └── Permissions: UC SELECT on all 16 gold tables           │ │
│  │                                                              │ │
│  │  API Scopes:                                                 │ │
│  │  ├── genie (read/write to Genie Space)                     │ │
│  │  ├── iam.access-control:read                               │ │
│  │  └── iam.current-user:read                                 │ │
│  │                                                              │ │
│  │  URL:                                                        │ │
│  │  └── https://tile-genie-7474645664849173.aws.databricks... │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Security & Permissions

```sql
-- Service Principal Permissions (Critical for App Functionality)

-- Catalog & Schema Access
GRANT USE CATALOG ON CATALOG tile_production_demo 
  TO `app-3nzv6y tile-genie`;

GRANT USE SCHEMA ON SCHEMA tile_production_demo.gold 
  TO `app-3nzv6y tile-genie`;

-- Table-Level SELECT Permissions (All 16 Tables)
GRANT SELECT ON TABLE tile_production_demo.gold.dim_customer 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_event 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_factory 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_machine 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_product 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_sales_rep 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_warehouse 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_crm_interaction 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_event_attendance 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_inventory_snapshot 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_machine_sensor_reading 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_machine_status_log 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_orders 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_production_daily 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_stock_transfer 
  TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.production_forecast 
  TO `app-3nzv6y tile-genie`;
```

---

## 6. Performance Architecture

### 6.1 Query Execution Timeline

```
Single Query Timeline (Sequential):
┌─────────────────────────────────────────────────────────────┐
│ NLP (5-10s) → SQL Gen (2-5s) → Warehouse (10-15s) →        │
│ → Execute (5-10s) → Format (2-5s) = ~30 seconds            │
└─────────────────────────────────────────────────────────────┘

Sequential Execution (BEFORE Optimization):
Query 1: ████████████████████████████████ (30s)
Query 2:                                 ████████████████████████████████ (30s)
Query 3:                                                                  ████████████████████████████████ (30s)
Total: 90 seconds ❌

Parallel Execution (AFTER Optimization):
Query 1: ████████████████████████████████ (30s)
Query 2: ████████████████████████████████ (30s)
Query 3: ████████████████████████████████ (30s)
Total: 30 seconds ✅ (3x faster!)
```

### 6.2 Parallel Execution Architecture

```python
# ThreadPoolExecutor Implementation

with ThreadPoolExecutor(max_workers=3) as executor:
    # Submit all 3 tasks simultaneously
    futures = {
        executor.submit(ask_genie, w, space_id, q1, None): q1,
        executor.submit(ask_genie, w, space_id, q2, None): q2,
        executor.submit(ask_genie, w, space_id, q3, None): q3
    }
    
    # Collect results as they complete (not in order)
    for future in as_completed(futures):
        result = future.result()
        # Display immediately when ready
        display_metric_card(result)

Benefits:
✅ 3x faster dashboard loading
✅ Better user experience (progressive loading)
✅ Efficient resource utilization
✅ Graceful error handling per query
```

### 6.3 Caching Strategy

```python
# WorkspaceClient Caching
@st.cache_resource
def get_workspace_client():
    """
    Cached at Streamlit resource level
    - Single instance per app session
    - Persists across page reloads
    - Avoids repeated authentication
    """
    return WorkspaceClient()

# Session State Management
st.session_state.conversation_id  # Persists Genie conversation
st.session_state.dashboard_loaded # Prevents dashboard reload
st.session_state.dashboard_data   # Caches dashboard results
st.session_state.messages         # Chat history
```

---

## 7. Architectural Decisions & Rationale

### 7.1 Key Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Parallel Query Execution** | Reduces load time from 90s → 30s | Increased complexity, concurrent API calls |
| **Auto-Loading Dashboard** | Showcases Genie immediately (contest requirement) | 30s initial load time |
| **Streamlit Framework** | Rapid development, native Databricks integration | Limited UI customization vs React |
| **Workspace Source Deployment** | More reliable than Git source (lesson learned) | Manual file updates vs Git workflow |
| **Minimal app.yaml** | Reduces deployment failures | Fewer configuration options |
| **ThreadPoolExecutor** | Python native, simple to implement | No async/await (overkill for 3 queries) |
| **Iterate ALL Attachments** | Genie returns multiple attachment types | Slight processing overhead |
| **Single WorkspaceClient** | Avoids auth overhead | Must be thread-safe (it is) |

### 7.2 Scalability Considerations

```yaml
Current Scale:
  - 16 tables (manageable for Genie)
  - 3 parallel queries (optimal for dashboard)
  - 1 Genie Space (single domain)
  - Medium compute (sufficient for demo)

Future Scale-Out Options:
  - Add more tables to Genie Space (up to 100s)
  - Increase parallel workers (5-10 queries)
  - Cache dashboard results (5-minute TTL)
  - Add multiple Genie Spaces (multi-domain)
  - Upgrade compute size (handle more concurrent users)
```

---

## 8. Error Handling Architecture

### 8.1 Error Recovery Flow

```python
try:
    # 1. Start Genie Conversation
    response = w.genie.start_conversation(space_id, content)
    
    # 2. Poll with Timeout Protection
    for attempt in range(60):  # Max 2 minutes
        message = w.genie.get_message(...)
        
        if status == 'COMPLETED':
            # 3. Extract with Fallback
            content = "No response"  # Default
            for attachment in message.attachments:
                if hasattr(attachment, 'text'):
                    content = attachment.text.content
            return {"success": True, "content": content}
        
        elif status == 'FAILED':
            # 4. Capture Genie Error
            return {"success": False, "error": message.error}
        
        time.sleep(2)
    
    # 5. Timeout Protection
    return {"success": False, "error": "Timeout after 2 minutes"}

except Exception as e:
    # 6. Catch-All Error Handler
    return {"success": False, "error": str(e)}
```

### 8.2 User-Facing Error Messages

```python
# Display user-friendly errors
if result["success"]:
    st.markdown(result["content"])
else:
    error = result.get("error", "Unknown error")
    
    if "PERMISSION_DENIED" in error:
        st.error("❌ Permission error: Service principal needs UC grants")
    elif "Timeout" in error:
        st.error("⏱️ Query timeout: Try a simpler question")
    elif "FAILED" in error:
        st.error(f"❌ Genie error: {error}")
    else:
        st.error(f"❌ Unexpected error: {error}")
```

---

## 9. Monitoring & Observability

### 9.1 Built-In Monitoring

```python
# Dashboard Load Time Tracking
start_time = time.time()
# ... execute queries ...
elapsed = time.time() - start_time
st.success(f"✅ Dashboard loaded in {elapsed:.1f}s (Parallel execution)")

# Progress Indicators
progress_bar = st.progress(0)
for idx, future in enumerate(as_completed(futures)):
    progress_bar.progress((idx + 1) / total_queries)
    st.caption(f"✅ Completed {idx + 1}/{total_queries} queries")

# Error Tracking
if not result["success"]:
    st.error(f"❌ Query failed: {result['error']}")
    # Could send to logging service here
```

### 9.2 Genie Space Monitoring

```
Monitoring URL (workspace-relative):
/genie/rooms/01f1a166e5891c2d89a0256412e7d452/monitoring

Tracked Metrics:
- Query success/failure rate
- Average response time
- Most common questions
- SQL queries generated
- User feedback (thumbs up/down)
```

---

## 10. Future Architecture Enhancements

### 10.1 Short-Term (Post-Contest)

```yaml
Dashboard Caching:
  - Cache results for 5 minutes
  - Instant dashboard after first load
  - TTL configurable per query type

Visualization Rendering:
  - Extract attachment.viz from Genie
  - Render charts directly in dashboard
  - Support bar, line, pie charts

Suggested Questions:
  - Display Genie's suggested follow-ups as clickable buttons
  - Context-aware next questions
  - Guided exploration workflow
```

### 10.2 Long-Term (Production)

```yaml
Multi-Space Support:
  - Switch between multiple Genie Spaces
  - Different domains (production, sales, quality)
  - Unified interface

Real-Time Alerts:
  - Scheduled Genie queries (daily/hourly)
  - Email/Slack notifications
  - Threshold-based alerts

Advanced Analytics:
  - Export SQL queries for reuse
  - Save favorite questions
  - Query history & bookmarks

Mobile Optimization:
  - Responsive design
  - Touch-friendly quick actions
  - Offline caching
```

---

## 11. Deployment Checklist

### 11.1 Pre-Deployment

```bash
✅ Update requirements.txt (databricks-sdk >= 0.33.0)
✅ Verify app.yaml syntax (minimal config)
✅ Test locally with GENIE_SPACE_ID env var
✅ Confirm service principal permissions (all 16 tables)
✅ Backup current working version
```

### 11.2 Deployment Commands

```bash
# Deploy to Databricks Apps
databricks apps deploy tile-genie   --source-code-path /Workspace/Users/ashish@.../TileGenie

# Verify deployment
databricks apps get tile-genie --output JSON

# Check logs if issues
databricks apps logs tile-genie
```

### 11.3 Post-Deployment Verification

```bash
✅ Open app URL (https://tile-genie-....databricksapps.com)
✅ Dashboard auto-loads in ~30 seconds
✅ Click quick action button (verify Genie response)
✅ Test chat interface (type custom question)
✅ Check SQL query display (expandable)
✅ Test reload dashboard button
✅ Verify no errors in sidebar
```

---

## 12. Architecture Diagram (ASCII)

```
┌───────────────────────────────────────────────────────────────────────────┐
│                        USER (Browser)                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  https://tile-genie-7474645664849173.aws.databricksapps.com        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │ HTTPS
┌────────────────────────────────────▼──────────────────────────────────────┐
│                     DATABRICKS APPS PLATFORM                               │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  TileGenie App (Streamlit)                                         │   │
│  │  Service Principal: app-3nzv6y tile-genie                         │   │
│  │  Compute: MEDIUM (Serverless)                                      │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐ │   │
│  │  │  app.py (Python 3.10+)                                       │ │   │
│  │  │  ┌────────────────────────────────────────────────────────┐ │ │   │
│  │  │  │  ThreadPoolExecutor (3 workers)                        │ │ │   │
│  │  │  │  - Query 1: "Yesterday's production?"        → Genie   │ │ │   │
│  │  │  │  - Query 2: "Machines down?"                 → Genie   │ │ │   │
│  │  │  │  - Query 3: "Current inventory?"             → Genie   │ │ │   │
│  │  │  └────────────────────────────────────────────────────────┘ │ │   │
│  │  │                                                                │ │   │
│  │  │  ┌────────────────────────────────────────────────────────┐ │ │   │
│  │  │  │  @st.cache_resource                                    │ │ │   │
│  │  │  │  WorkspaceClient (databricks-sdk >= 0.33.0)           │ │ │   │
│  │  │  └────────────────────────────────────────────────────────┘ │ │   │
│  │  └──────────────────────────────────────────────────────────────┘ │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │ Genie API (databricks-sdk)
┌────────────────────────────────────▼──────────────────────────────────────┐
│                      DATABRICKS GENIE SERVICE                              │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  Genie Space: TileGenie Production Intelligence                    │   │
│  │  ID: 01f1a166e5891c2d89a0256412e7d452                              │   │
│  │                                                                      │   │
│  │  NLP Engine → SQL Generator → Query Executor → Response Formatter  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │ SQL Queries
┌────────────────────────────────────▼──────────────────────────────────────┐
│                      UNITY CATALOG                                         │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  Catalog: tile_production_demo                                     │   │
│  │  Schema: gold                                                       │   │
│  │                                                                      │   │
│  │  Tables (16):                                                       │   │
│  │  - 7 Dimension Tables (customer, factory, machine, product...)    │   │
│  │  - 8 Fact Tables (production, orders, inventory, sensors...)      │   │
│  │  - 1 Analytical Table (production_forecast)                        │   │
│  │                                                                      │   │
│  │  Permissions: Service Principal has SELECT on all tables           │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬──────────────────────────────────────┘
                                     │ Query Execution
┌────────────────────────────────────▼──────────────────────────────────────┐
│                      SQL WAREHOUSE                                         │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │  - Executes generated SQL                                          │   │
│  │  - Returns results to Genie                                        │   │
│  │  - Auto-scaling for performance                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

TileGenie demonstrates a production-ready architecture for Genie-powered applications:

**Key Strengths:**
✅ Auto-loading dashboard showcases immediate AI value
✅ Parallel execution (3x performance improvement)
✅ Clean separation of concerns (UI → Logic → API → Data)
✅ Robust error handling at every layer
✅ Streamlit caching for optimal performance
✅ Comprehensive permissions model
✅ Scalable design for future enhancements

**Contest Differentiators:**
🏆 "Genie at the Core" - All intelligence from Genie, not static SQL
🏆 Transparent SQL generation (builds trust)
🏆 Real-time progress indicators (shows AI working)
🏆 Executive-focused use case (practical business value)
🏆 Technical sophistication (parallel execution, proper SDK usage)

**Production Readiness:**
📊 Battle-tested through multiple deployment iterations
📊 Comprehensive error handling and user feedback
📊 Security-first design (service principal with least privilege)
📊 Monitoring and observability built-in
📊 Clear path to future enhancements

---

**Architecture Version:** 1.0
**Last Updated:** August 27, 2026
**Status:** ✅ Production Deployed
