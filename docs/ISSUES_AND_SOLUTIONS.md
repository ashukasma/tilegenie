# TileGenie: Issues & Solutions Documentation
**Databricks Community Contest - Genie-Powered App Challenge**

## Project Overview
- **App Name:** TileGenie - Genie-Powered Production Intelligence
- **Genie Space ID:** 01f1a166e5891c2d89a0256412e7d452
- **Data:** 16 gold tables (tile_production_demo.gold.*)
- **Service Principal:** app-3nzv6y tile-genie (ID: 73721084961770)
- **App URL:** https://tile-genie-7474645664849173.aws.databricksapps.com

---

## Issues & Solutions Timeline

### 1. ❌ Initial Deployment Failures (HTTP/Routing Level)

**Issue:**
- Backend deployments succeeded
- Apps HTTP level failed with 502/504 errors
- Workspace platform routing/proxy bugs

**Root Cause:**
- Workspace infrastructure issues with Git source deployments
- Complex app.yaml configurations causing routing problems

**Solution:**
✅ Switched from Git source to workspace source
✅ Adopted minimal app.yaml pattern from working "hello-world" app
✅ Simplified configuration to essential elements only

**Files Modified:**
- `app.yaml`: Removed complex port configurations, kept only essential Genie binding

---

### 2. ❌ ModuleNotFoundError: Genie SDK Missing

**Issue:**
```
ModuleNotFoundError: No module named 'databricks.sdk.service.genie'
```

**Root Cause:**
- Outdated databricks-sdk version in requirements.txt
- Genie SDK requires version >= 0.33.0

**Solution:**
✅ Updated requirements.txt:
```
databricks-sdk>=0.33.0
streamlit~=1.38.0
```

**Verification:**
```bash
pip show databricks-sdk  # Confirmed >= 0.33.0
```

---

### 3. ❌ Permissions Error: Unity Catalog Access Denied

**Issue:**
```
Error: PERMISSION_DENIED - Service principal lacks SELECT on tile_production_demo.gold tables
```

**Root Cause:**
- Service principal (app-3nzv6y tile-genie, ID: 73721084961770) had no UC permissions
- Apps require explicit grants to query data

**Solution:**
✅ Granted comprehensive Unity Catalog permissions:
```sql
-- Catalog and schema access
GRANT USE CATALOG ON CATALOG tile_production_demo TO `app-3nzv6y tile-genie`;
GRANT USE SCHEMA ON SCHEMA tile_production_demo.gold TO `app-3nzv6y tile-genie`;

-- Table SELECT permissions (all 16 gold tables)
GRANT SELECT ON TABLE tile_production_demo.gold.dim_customer TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_event TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_factory TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_machine TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_product TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_sales_rep TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.dim_warehouse TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_crm_interaction TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_event_attendance TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_inventory_snapshot TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_machine_sensor_reading TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_machine_status_log TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_orders TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_production_daily TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.fact_stock_transfer TO `app-3nzv6y tile-genie`;
GRANT SELECT ON TABLE tile_production_demo.gold.production_forecast TO `app-3nzv6y tile-genie`;
```

**Verification:**
```sql
SHOW GRANTS ON TABLE tile_production_demo.gold.fact_production_daily;
-- Confirmed service principal has SELECT
```

---

### 4. ❌ App Logic Bug: Response Attribute Error

**Issue:**
```python
AttributeError: 'GenieMessage' object has no attribute 'id'
```

**Root Cause:**
- Used `response.id` instead of correct `response.message_id`
- Incorrect SDK API usage

**Solution:**
✅ Fixed response handling:
```python
# BEFORE (Wrong)
message_id = response.id

# AFTER (Correct)
message_id = response.message_id
```

---

### 5. ❌ Empty Responses: Attachments Not Extracted

**Issue:**
- App showed "No response" despite Genie returning valid answers
- Only checking first attachment

**Root Cause:**
- Genie responses contain multiple attachments (text, SQL, visualizations, suggestions)
- Code only checked first attachment, missed text answers in later attachments

**Solution:**
✅ Iterate through ALL attachments:
```python
# BEFORE (Wrong)
if message.attachments:
    attachment = message.attachments[0]
    if hasattr(attachment, 'text'):
        content = attachment.text.content

# AFTER (Correct)
if message.attachments:
    for attachment in message.attachments:
        if hasattr(attachment, 'text') and attachment.text:
            if hasattr(attachment.text, 'content'):
                content = attachment.text.content
        if hasattr(attachment, 'query') and attachment.query:
            if hasattr(attachment.query, 'query'):
                sql_query = attachment.query.query
```

**Lesson:**
- Genie responses are rich objects with multiple attachment types
- Always iterate ALL attachments to find text/SQL/visualizations

---

### 6. ❌ WorkspaceClient Initialization Issues

**Issue:**
- Multiple WorkspaceClient instances causing auth problems
- Unstable connections

**Root Cause:**
- Creating new client on every request
- Not using Streamlit caching

**Solution:**
✅ Cached WorkspaceClient with @st.cache_resource:
```python
@st.cache_resource
def get_workspace_client():
    from databricks.sdk import WorkspaceClient
    return WorkspaceClient()

# Use single cached instance
w = get_workspace_client()
```

---

### 7. ⚠️ Performance Issue: Slow Dashboard Loading

**Issue:**
- Dashboard took 90 seconds to load (3 queries × 30s each)
- Sequential execution

**Root Cause:**
- Genie queries executed one at a time:
  1. Query 1: 30s
  2. Query 2: 30s
  3. Query 3: 30s
  4. **Total: 90s**

**Why Each Query Takes ~30 Seconds:**
1. Natural Language Processing (5-10s)
2. SQL Generation (2-5s)
3. SQL Warehouse Cold Start (10-15s, first query)
4. Query Execution (5-10s)
5. Response Formatting (2-5s)

**Solution:**
✅ Implemented parallel execution with ThreadPoolExecutor:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

# Execute all 3 queries in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(ask_genie, w, GENIE_SPACE_ID, q, None): q 
               for q in ceo_questions}
    
    for future in as_completed(futures):
        result = future.result()
        results.append(result)
```

**Performance Improvement:**
- Before: 90 seconds (sequential)
- After: ~30 seconds (parallel)
- **3x faster! ⚡**

---

### 8. ✅ Enhancement: Auto-Loading Dashboard

**Requirement:**
- Showcase "Genie at the Core" for contest
- Dashboard should load automatically on app startup
- Demonstrate Genie's intelligence immediately

**Implementation:**
```python
if not st.session_state.dashboard_loaded:
    # Auto-load 3 CEO questions in parallel
    ceo_questions = [
        "What was yesterday's total production in units?",
        "How many machines are currently down or in maintenance?",
        "What is the current total inventory across all warehouses?"
    ]
    
    # Parallel execution (30 seconds total)
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Execute all queries simultaneously
        futures = {executor.submit(ask_genie, w, GENIE_SPACE_ID, q, None): q 
                   for q in ceo_questions}
        
        # Display results as dashboard cards
        for future in as_completed(futures):
            result = future.result()
            display_metric_card(result)
```

**Features:**
✅ Auto-loads on first page visit
✅ Shows progress bar during loading
✅ Displays results as dashboard cards
✅ Shows SQL queries Genie generated
✅ "Reload Dashboard" button in sidebar

---

## Final Architecture

### App Structure
```
TileGenie/
├── app.py              # Main Streamlit app (parallel execution)
├── app.yaml            # Minimal config (Genie space binding)
├── requirements.txt    # Dependencies (databricks-sdk >=0.33.0)
└── backups/
    ├── app_working_backup.py
    └── app_enhanced.py
```

### Key Components

**1. Genie Integration**
```python
# Initialize cached client
w = get_workspace_client()

# Ask Genie (with polling)
def ask_genie(w, space_id, question, conversation_id=None):
    response = w.genie.start_conversation(...)
    
    # Poll until COMPLETED
    for _ in range(60):
        message = w.genie.get_message(...)
        if status == 'COMPLETED':
            # Extract text and SQL from ALL attachments
            return result
```

**2. Parallel Dashboard Loading**
```python
# Execute 3 queries simultaneously
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(ask_genie, ...): q 
               for q in ceo_questions}
    
    # Collect results as they complete
    for future in as_completed(futures):
        result = future.result()
```

**3. UI Components**
- 📊 Auto-loading dashboard (3 metric cards)
- ⚡ Quick Action Buttons (4 CEO queries)
- 💬 Chat interface
- 🔍 SQL transparency (expandable queries)
- 🔄 Reload Dashboard button

---

## Key Learnings

### 1. Databricks Apps Deployment
- ✅ Workspace source is more reliable than Git source
- ✅ Keep app.yaml minimal (only essential configurations)
- ✅ Follow working patterns (hello-world app)

### 2. Genie SDK Best Practices
- ✅ Use databricks-sdk >= 0.33.0
- ✅ Cache WorkspaceClient with @st.cache_resource
- ✅ Iterate ALL attachments (not just first one)
- ✅ Use response.message_id (not response.id)
- ✅ Poll with timeout (60 × 2s = 2 minutes max)

### 3. Permissions
- ✅ Service principals need explicit UC grants
- ✅ Grant USE CATALOG, USE SCHEMA, and SELECT
- ✅ Verify with SHOW GRANTS

### 4. Performance
- ✅ Parallel execution for multiple queries
- ✅ ThreadPoolExecutor for concurrent Genie calls
- ✅ ~30 seconds per query is normal (NLP + SQL + execution)

### 5. Contest Strategy
- ✅ Auto-loading dashboard showcases "Genie at the Core"
- ✅ SQL transparency demonstrates Genie's intelligence
- ✅ Progress bars show real-time AI work
- ✅ Parallel execution shows technical sophistication

---

## Troubleshooting Checklist

### If App Fails to Start:
1. Check app.yaml syntax (YAML formatting)
2. Verify GENIE_SPACE_ID is correct
3. Check requirements.txt has databricks-sdk>=0.33.0
4. Review app logs: `databricks apps logs tile-genie`

### If Permissions Error:
1. Verify service principal name: `app-3nzv6y tile-genie`
2. Run SHOW GRANTS on all tables
3. Grant missing permissions with GRANT statements above

### If Empty Responses:
1. Check ALL attachments are being iterated
2. Verify response.message_id (not response.id)
3. Add debug logging to see attachment types

### If Slow Performance:
1. Verify parallel execution is enabled (ThreadPoolExecutor)
2. Check max_workers=3 (not sequential loop)
3. Monitor with progress bar/timer

---

## Success Metrics

### Technical
✅ App deploys successfully
✅ Genie queries execute without errors
✅ Dashboard loads in ~30 seconds
✅ Service principal has all permissions
✅ Chat interface responds correctly

### Contest Requirements
✅ "Genie at the Core" - Auto-loading dashboard proves Genie intelligence
✅ Natural language → SQL transparency
✅ Real-time progress indicators
✅ Scalable architecture (parallel execution)
✅ Rich UI (dashboard cards, quick actions, chat)

---

## Production Readiness

### Current Status: ✅ Contest-Ready

**Strengths:**
- Robust error handling
- Permission audit complete
- Performance optimized (3x faster)
- Auto-loading demonstrates value immediately
- SQL transparency builds trust

**Known Limitations:**
- ~30s per Genie query is inherent (NLP + execution)
- First warehouse cold start adds 10-15s
- Parallel execution mitigates but doesn't eliminate latency

**Future Enhancements (Post-Contest):**
- Cache dashboard results for 5 minutes
- Add more visualization types from Genie responses
- Implement suggested questions as clickable buttons
- Add export functionality for SQL queries
- Performance metrics tracking

---

## Contest Submission Summary

**App Name:** TileGenie  
**Category:** Genie-Powered App Challenge  
**Core Value:** Auto-loading production intelligence dashboard  

**Genie Integration:**
- ✅ Natural language to SQL
- ✅ Real-time data analysis across 16 gold tables
- ✅ Transparent SQL generation
- ✅ Auto-loading dashboard on startup
- ✅ Parallel execution for performance

**Technical Innovation:**
- ✅ ThreadPoolExecutor for concurrent Genie queries
- ✅ Progress tracking during dashboard load
- ✅ Comprehensive error handling
- ✅ Streamlit caching for WorkspaceClient

**User Experience:**
- ✅ Zero-click intelligence (auto-loads on startup)
- ✅ CEO-level insights immediately visible
- ✅ Quick action buttons for common questions
- ✅ Chat interface for exploratory analysis
- ✅ SQL transparency for trust and debugging

---

**Document Generated:** August 27, 2026  
**Version:** 1.0 - Final Contest Submission  
**Status:** ✅ Production Deployment Successful
