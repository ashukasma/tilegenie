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
    page_icon="🧞",
    layout="wide"
)

# Palette follows Vastu colour guidance: ivory base (peace/purity), green primary
# (growth, N/E), turmeric gold accent (prosperity, NE), terracotta only for alerts.
# No pure black, no dominant red.
st.markdown("""
<style>
:root {
    --ivory:#FCFAF5; --sand:#F4EFE5; --clay:#E4D9C6;
    --ink:#2E2B26; --muted:#7A7060;
    --emerald:#1B7A5A; --emerald-dark:#145C44; --emerald-soft:#E7F1EC; --emerald-line:#CFE3D9;
    --gold:#C9962C; --gold-soft:#F7EEDA;
    --terracotta:#B5502E; --terracotta-dark:#8A3B1F;
}

#MainMenu, footer, [data-testid="stHeader"] { display: none; }
.block-container { padding-top: 2.2rem; padding-bottom: 6rem; max-width: 1180px; }

/* ---- header ---- */
.tg-brand { display:flex; align-items:center; gap:.9rem; }
.tg-mark { display:grid; grid-template-columns:repeat(2,15px); grid-template-rows:repeat(2,15px); gap:3px; }
.tg-mark i { border-radius:3px; display:block; }
.tg-mark i:nth-child(1){ background:var(--emerald); }
.tg-mark i:nth-child(2){ background:var(--gold); }
.tg-mark i:nth-child(3){ background:var(--clay); }
.tg-mark i:nth-child(4){ background:var(--emerald-dark); }
.tg-name { font-size:1.65rem; font-weight:700; letter-spacing:-.02em; color:var(--ink); line-height:1.15; }
.tg-tag { font-size:.83rem; color:var(--muted); margin-top:.15rem; }
.tg-rule { height:3px; border-radius:2px; margin:1rem 0 1.7rem;
    background:linear-gradient(90deg,var(--emerald) 0%,var(--gold) 38%,var(--clay) 100%); }

@media (max-width: 640px) {
    .tg-name { font-size:1.4rem; }
    .tg-rule { margin:.8rem 0 1.3rem; }
}

/* ---- section label ---- */
.tg-sec { font-size:.71rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase;
    color:var(--muted); margin:0 0 .8rem; }
.tg-sec span { color:var(--clay); font-weight:600; letter-spacing:.04em; text-transform:none; }

/* ---- KPI cards ----
   :has() matches every ancestor, so exclude any wrapper that holds a *nested*
   marked wrapper. That leaves exactly the innermost one: the card itself. */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) {
    background:#FFFFFF; border:1px solid var(--clay); border-top:3px solid var(--gold);
    border-radius:12px; padding:1.2rem 1.3rem 1.1rem;
    flex:1; display:flex; flex-direction:column;
    box-shadow:0 1px 2px rgba(46,43,38,.05), 0 6px 18px rgba(46,43,38,.045);
}
/* Equal-height cards. Every rule below carries the same :not() guard as the card
   itself -- an unguarded :has(.tg-card) also matches the outer page wrapper and
   restacks the whole layout. */
div[data-testid="column"]:has(.tg-card) { display:flex; flex-direction:column; }
div[data-testid="column"]:has(.tg-card) > div[data-testid="stVerticalBlockBorderWrapper"] { flex:1; display:flex; flex-direction:column; }

div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) > div,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) > div > [data-testid="stVerticalBlock"] {
    flex:1; display:flex; flex-direction:column;
}
/* the SQL button drops to the card floor, hard right */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .element-container:has(.stButton),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) [data-testid="element-container"]:has(.stButton),
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton { margin-top:auto; align-self:flex-end; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton { display:flex; justify-content:flex-end; width:100%; }

/* SQL is a debug affordance: a small square icon, not a call to action */
.tg-sqlbtn > button,
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton button,
[data-testid="stChatMessage"] .stButton button {
    width:30px; height:30px; min-height:0; padding:0;
    display:inline-flex; align-items:center; justify-content:center;
    color:var(--muted); background:transparent;
    border:1px solid var(--clay); border-radius:8px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton button:hover,
[data-testid="stChatMessage"] .stButton button:hover {
    color:var(--emerald-dark); border-color:var(--emerald); background:var(--emerald-soft);
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton button span[role="img"],
[data-testid="stChatMessage"] .stButton button span[role="img"] { font-size:17px; line-height:1; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) .stButton button p,
[data-testid="stChatMessage"] .stButton button p { margin:0; line-height:1; }

/* ---- alerts ----
   Both failure states (a KPI question that failed, a chat answer that failed)
   mean the same thing, so they read the same: terracotta, the one warm alert
   colour this palette allows. */
[data-testid="stAlertContainer"] {
    background:rgba(181,80,46,.08) !important;
    color:var(--terracotta-dark) !important;
    border:1px solid rgba(181,80,46,.22);
    border-radius:10px;
}
[data-testid="stAlertContainer"] code { color:var(--terracotta-dark); background:rgba(181,80,46,.1); }

/* ---- SQL dialog ---- */
[data-testid="stDialog"] div[role="dialog"] { background:var(--ivory); border:1px solid var(--clay); border-radius:14px; }
[data-testid="stDialog"] code { font-size:.85rem; }

/* ---- chat empty state ---- */
.tg-empty { text-align:center; color:var(--muted); font-size:.88rem; line-height:1.6;
    border:1px dashed var(--clay); border-radius:12px; padding:2rem 1.5rem; background:rgba(255,255,255,.5); }
.tg-empty b { color:var(--ink); font-weight:600; }

.tg-card-label { font-size:.69rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
    color:var(--muted); margin-bottom:.15rem; }
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) p {
    font-size:.97rem; line-height:1.6; color:var(--ink); margin-bottom:.4rem;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.tg-card):not(:has(div[data-testid="stVerticalBlockBorderWrapper"] .tg-card)) strong {
    color:var(--emerald-dark); font-weight:700;
}

/* ---- buttons ---- */
.stButton button {
    background:#FFFFFF; color:var(--emerald-dark); border:1px solid var(--clay);
    border-radius:999px; font-weight:600; font-size:.84rem; padding:.45rem 1rem;
    transition:border-color .15s ease, background .15s ease;
}
.stButton button:hover { border-color:var(--emerald); background:var(--emerald-soft); color:var(--emerald-dark); }
.stButton button:focus:not(:active) { border-color:var(--emerald); color:var(--emerald-dark); }
.stButton button[kind="primary"] { background:var(--emerald); color:#fff; border-color:var(--emerald); }
.stButton button[kind="primary"]:hover { background:var(--emerald-dark); border-color:var(--emerald-dark); color:#fff; }


/* ---- expander ---- */
[data-testid="stExpander"] details { border:1px solid var(--clay); border-radius:9px; background:var(--ivory); }
[data-testid="stExpander"] summary { font-size:.78rem; font-weight:600; color:var(--muted); }
[data-testid="stExpander"] summary:hover { color:var(--emerald-dark); }

/* ---- progress ---- */
.stProgress > div > div > div > div { background:linear-gradient(90deg,var(--gold),var(--emerald)); }

/* ---- chat ---- */
/* the bottom bar sits outside .block-container, so cap it to match the content column */
[data-testid="stBottomBlockContainer"] { max-width:1180px; margin:0 auto; padding-bottom:1.5rem; }
[data-testid="stChatInput"] { border:1px solid var(--clay); border-radius:14px; background:#fff; }
[data-testid="stChatMessage"] { background:transparent; padding:.6rem 0; }
[data-testid="stChatMessageAvatarUser"] { background-color:var(--emerald) !important; color:#fff !important; }
[data-testid="stChatMessageAvatarAssistant"] { background-color:var(--gold) !important; color:#fff !important; }
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

@st.dialog("Generated SQL", width="large")
def show_sql(question, sql):
    """SQL is a developer concern, so it lives behind a modal rather than in the card."""
    st.caption(question)
    st.code(sql, language="sql")


GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID", "").replace("genie://", "")

if not GENIE_SPACE_ID:
    st.error("GENIE_SPACE_ID is not configured.")
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
head_left, head_right = st.columns([5, 1], vertical_alignment="center")
with head_left:
    st.markdown("""
    <div class="tg-brand">
      <div class="tg-mark"><i></i><i></i><i></i><i></i></div>
      <div>
        <div class="tg-name">TileGenie</div>
        <div class="tg-tag">Production intelligence for tile manufacturing, powered by Databricks Genie</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with head_right:
    if st.button("Reload", use_container_width=True, help="Re-run the executive questions and clear the chat"):
        st.session_state.dashboard_loaded = False
        st.session_state.dashboard_data = []
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
st.markdown('<div class="tg-rule"></div>', unsafe_allow_html=True)

# Auto-load dashboard on first load (PARALLEL EXECUTION)
CEO_QUESTIONS = [
    ("Yesterday's Production", "What was yesterday's total production in units?"),
    ("Machines Down", "How many machines are currently down or in maintenance?"),
    ("Total Inventory", "What is the current total inventory across all warehouses?"),
]

if not st.session_state.dashboard_loaded:
    st.markdown('<div class="tg-sec">Executive Dashboard</div>', unsafe_allow_html=True)

    w = get_workspace_client()
    questions = [q for _, q in CEO_QUESTIONS]

    progress = st.progress(0.0, text=f"Asking Genie {len(questions)} questions in parallel...")

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=len(questions)) as executor:
        futures = [executor.submit(ask_genie, w, GENIE_SPACE_ID, q, None) for q in questions]

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            progress.progress(
                len(results) / len(questions),
                text=f"Answered {len(results)} of {len(questions)}",
            )
            if result["success"] and st.session_state.conversation_id is None:
                st.session_state.conversation_id = result["conversation_id"]

    elapsed = time.time() - start_time
    progress.empty()

    st.session_state.dashboard_data = sorted(results, key=lambda x: questions.index(x["question"]))
    st.session_state.dashboard_loaded = True
    st.session_state.load_seconds = elapsed
    st.rerun()

# The dashboard and the chat each live in their own fragment. A widget inside a
# fragment re-runs only that fragment, so clicking a suggested question or a SQL
# icon no longer re-executes the whole script and repaints the entire page.
@st.fragment
def dashboard_panel():
    meta = ""
    if st.session_state.get("load_seconds"):
        meta = f"<span>&nbsp;&nbsp;/&nbsp;&nbsp;{len(CEO_QUESTIONS)} parallel Genie queries in {st.session_state.load_seconds:.1f}s</span>"
    st.markdown(f'<div class="tg-sec">Executive Dashboard{meta}</div>', unsafe_allow_html=True)

    for col, (label, _), data in zip(st.columns(3, gap="medium"), CEO_QUESTIONS, st.session_state.dashboard_data):
        with col, st.container(border=False):
            st.markdown(
                f'<span class="tg-card"></span><div class="tg-card-label">{label}</div>',
                unsafe_allow_html=True,
            )
            if data["success"]:
                st.markdown(data["content"])
                if data.get("sql"):
                    # icon-only, but :material/: renders an aria-label so it keeps an accessible name
                    if st.button(":material/code:", key=f"sql_kpi_{label}", help="Show the SQL Genie generated"):
                        show_sql(label, data["sql"])
            else:
                st.warning(data.get("error", "Unknown error"))

    st.write("")


QUICK_ACTIONS = [
    ("Production Trends", "Show me production trends for the last 7 days"),
    ("Low Stock", "Which products have the lowest stock levels?"),
    ("Forecast", "What is the expected production for next quarter?"),
    ("Machine Downtime", "Which machines had the most downtime this week?"),
]


@st.fragment
def chat_panel():
    st.markdown('<div class="tg-sec">Ask Genie<span>&nbsp;&nbsp;/&nbsp;&nbsp;suggested questions</span></div>', unsafe_allow_html=True)
    for col, (label, question) in zip(st.columns(len(QUICK_ACTIONS), gap="small"), QUICK_ACTIONS):
        if col.button(label, use_container_width=True):
            # no st.rerun(): these buttons render before the pop below, so the
            # question is picked up in this same pass.
            st.session_state["pending_question"] = question

    st.write("")

    pending = st.session_state.pop("pending_question", None)

    if not st.session_state.messages and not pending:
        st.markdown(
            '<div class="tg-empty">Pick a question above, or ask your own below.<br>'
            'Genie writes the SQL and answers from your <b>16 gold tables</b>.</div>',
            unsafe_allow_html=True,
        )

    for idx, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("error"):
                st.error(msg["content"])
            else:
                st.markdown(msg["content"])

            if msg["role"] == "assistant" and msg.get("sql"):
                if st.button(":material/code:", key=f"sql_msg_{idx}", help="Show the SQL Genie generated"):
                    show_sql(st.session_state.messages[idx - 1]["content"] if idx else "", msg["sql"])

    if pending:
        w = get_workspace_client()

        st.session_state.messages.append({"role": "user", "content": pending})
        with st.chat_message("user"):
            st.markdown(pending)

        with st.chat_message("assistant"), st.spinner("Genie is analyzing..."):
            result = ask_genie(w, GENIE_SPACE_ID, pending, st.session_state.conversation_id)

        if result["success"]:
            if st.session_state.conversation_id is None:
                st.session_state.conversation_id = result["conversation_id"]
            answer = {"role": "assistant", "content": result["content"]}
            if result.get("sql"):
                answer["sql"] = result["sql"]
        else:
            answer = {"role": "assistant", "content": result.get("error", "Unknown error"), "error": True}

        st.session_state.messages.append(answer)
        # App scope, not scope="fragment", on purpose. A fragment-scoped rerun here
        # re-runs only this panel, and any click that arrived on the *dashboard*
        # fragment while Genie was working is consumed without that fragment ever
        # running -- so its "View SQL" dialog silently never opened. Costs one full
        # rerun per answer, hidden behind the query latency.
        st.rerun()


# Chat input stays at top level: inside a fragment Streamlit renders it inline
# instead of pinning it to the bottom of the page.
typed = st.chat_input("Ask Genie about your tile production...")
if typed:
    st.session_state["pending_question"] = typed

if st.session_state.dashboard_loaded and st.session_state.dashboard_data:
    dashboard_panel()

chat_panel()
