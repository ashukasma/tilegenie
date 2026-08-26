# 🟦 TileGenie - Genie-Powered Production Intelligence

**Entry for Databricks Community Contest: Genie-Powered App Challenge**  
**Track A: Real-World Problem Solver**

> *"Ask your factory floor anything."*

---

## 🎯 Problem Statement

Tile manufacturing companies face a critical operational intelligence gap:

- **Data silos:** Production data (factories), inventory data (warehouses), CRM data, and ERP data live in disconnected systems
- **Manual reporting:** Leadership waits hours or days for basic answers like "Why was production reduced yesterday?"
- **No self-service:** Non-technical executives can't explore their own data without SQL knowledge

**TileGenie solves this** by unifying all operational data in Unity Catalog and letting leadership ask questions in plain English through a Genie-powered conversational interface.

---

## ✨ Why Genie is at the Core

**The gut check:** If you removed Genie, would the main experience break?

**Answer: YES.** 

- TileGenie has **NO static dashboards or fixed reports**
- The **only way** to get insights is through natural language conversation with Genie
- The summary metrics at the top are lightweight orientation — they don't answer the CEO's questions
- **Every business question** flows through Genie's SQL generation and reasoning

Genie isn't a feature — it's the entire experience.

---

## 📦 What's Included

```
TileGenie/
├── app.py                      # Main Streamlit application
├── app.yaml                    # Databricks App configuration
├── requirements.txt            # Python dependencies
├── scripts/
│   └── generate_tile_production_data.py  # Synthetic data generator (16 tables)
└── docs/
    └── genie_agent_configuration.md     # Complete Genie Agent setup guide
```

---

## 🛠️ Setup Instructions

### Prerequisites

- Databricks workspace (Free Edition compatible)
- Access to create Unity Catalog tables
- Serverless SQL warehouse

### Step 1: Generate Synthetic Data

Run the data generator to create 16 Delta tables:

```bash
# From a Databricks notebook or terminal
python /Workspace/Users/<your-email>/TileGenie/scripts/generate_tile_production_data.py
```

This creates:
- **Catalog:** `tile_production_demo`
- **Schema:** `gold`
- **Tables:** 16 tables (7 dimensions + 9 facts)
- **Data:** 180 days of synthetic tile manufacturing history

**Key business rule embedded:** Machines have mandatory cooldown cycles (max continuous run hours + cooldown hours). The status logs reflect Running → Scheduled Cooldown cycles with occasional Breakdowns and Idle periods.

### Step 2: Create the Genie Agent

1. **Navigate to Genie Spaces** in your Databricks workspace
2. **Create a new Space** named "TileGenie Production Intelligence"
3. **Add all 16 tables** from `tile_production_demo.gold`:
   - Dimensions: dim_warehouse, dim_factory, dim_machine, dim_product, dim_customer, dim_event, dim_sales_rep
   - Facts: fact_machine_status_log, fact_machine_sensor_reading, fact_production_daily, production_forecast, fact_inventory_snapshot, fact_stock_transfer, fact_crm_interaction, fact_orders, fact_event_attendance

4. **Configure the Genie Agent:**
   - Copy the **Instructions** from `docs/genie_agent_configuration.md`
   - Add all **10 sample questions**
   - Add all **4 verified answers** (the critical CEO questions)

5. **Test the Genie Agent** directly in the Genie UI with these questions:
   - "Why was production reduced on [recent date] at Factory 1?"
   - "What is the expected production for next quarter?"
   - "How much stock do we have in each warehouse?"
   - "What should our production plan be for Q4 2026?"

6. **Note the Genie Space ID** (you'll need it in the next step)

📖 **See `docs/genie_agent_configuration.md` for the complete configuration text.**

### Step 3: Configure the App

Edit `app.yaml` and replace the placeholder with your actual Genie Space ID:

```yaml
env:
  - name: GENIE_SPACE_ID
    value: "genie://<YOUR_ACTUAL_GENIE_SPACE_ID>"

resources:
  - name: tilegenie_agent
    genie_space:
      genie_space_id: "<YOUR_ACTUAL_GENIE_SPACE_ID>"
```

### Step 4: Deploy the App

#### Option A: Local Testing (Recommended First)

```bash
cd /Workspace/Users/<your-email>/TileGenie
databricks apps run-local .
```

This starts the app locally on `http://localhost:8501`

#### Option B: Deploy to Databricks Apps

1. **From the Databricks UI:**
   - Navigate to **Apps** → **Create App**
   - Select the `TileGenie` folder
   - Databricks will automatically detect `app.yaml`
   - Click **Deploy**

2. **From the CLI:**

```bash
databricks apps deploy TileGenie \
  --source-code-path /Workspace/Users/<your-email>/TileGenie
```

3. **Access your app** at the URL provided after deployment

---

## 🎯 Core Demo Questions (Must Work Flawlessly)

These 4 questions are the contest demo — test them thoroughly:

1. **"Why was production reduced yesterday?"**
   - Expected: Joins production_daily to machine_status_log, shows actual reasons (Breakdown, Cooldown, Idle)

2. **"What is the expected production of Porcelain-Glossy-24x24 for next quarter?"**
   - Expected: Queries production_forecast table, shows forecast with confidence bounds

3. **"What should our production plan be for Q4 2026?"**
   - Expected: Shows all products' forecasts for Q4, sorted by projected revenue

4. **"How much stock do we have in each warehouse?"**
   - Expected: Queries latest inventory snapshot, groups by warehouse, flags low stock

---

## 🏆 Contest Alignment

### Judging Criteria (40 points total)

| Criterion | Points | How TileGenie Scores |
|-----------|--------|---------------------|
| **Genie at the Core** | 20 | ✅ Chat is the ONLY way to get insights. No Genie = broken app. |
| **Track A Execution** | 10 | ✅ Solves real operational intelligence gap for manufacturing leadership. |
| **App Experience** | 10 | ✅ Polished UI, branded styling, intuitive chat flow, structured data rendering. |

### Theme: "Genie at the Core"

✅ **Central:** Genie powers 100% of data exploration  
✅ **Meaningful:** Answers questions leadership currently can't self-serve  
✅ **Effective:** Pre-configured with verified SQL for critical questions  

---

## 📊 App Features

### 1. Chat-First Intelligence
- **Natural language** questions about production, inventory, machines, sales
- **Multi-turn conversations** with context retention
- **Structured responses** rendered as tables and charts

### 2. Lightweight Summary Strip
- Today's production vs. plan
- Machine efficiency
- Active machines count
- Low stock alerts

*(Summary is orientation only — not a substitute for chat)*

### 3. Admin Utilities
- **Regenerate Data:** Re-run synthetic data generator from within the app
- **Pull Data:** Simulated ingestion pattern (shows how real feeds would work)
- **Clear Chat:** Start a fresh conversation

### 4. Branded Experience
- Custom CSS styling (not default Streamlit)
- Blue gradient header with TileGenie branding
- Clean metric cards and chat bubbles

---

## 💾 Data Model Summary

### Dimensions (7 tables)
- **dim_warehouse:** 5 warehouses across India
- **dim_factory:** 3 factories (Morbi, Jaipur, Chennai)
- **dim_machine:** 13-18 machines per factory with cooldown rules
- **dim_product:** 12 tile products (Porcelain, Ceramic, Vitrified, Mosaic)
- **dim_customer:** 50 customers (Dealers, Builders, Retailers)
- **dim_event:** 6 trade shows/exhibitions
- **dim_sales_rep:** 8 sales representatives

### Facts (9 tables)

**IoT/Machine:**
- **fact_machine_status_log:** Machine state timeline (Running, Cooldown, Breakdown, Idle) with reason codes
- **fact_machine_sensor_reading:** Hourly sensor data (temperature, vibration, power, humidity)

**Production:**
- **fact_production_daily:** Daily production by factory/product (planned vs actual, defects, downtime)
- **production_forecast:** Pre-computed quarterly forecasts (don't forecast live!)

**Inventory:**
- **fact_inventory_snapshot:** Weekly warehouse stock levels
- **fact_stock_transfer:** Inter-warehouse transfers

**CRM/Sales:**
- **fact_crm_interaction:** Customer interactions by sales reps
- **fact_orders:** Orders with values and status
- **fact_event_attendance:** Customer attendance at trade shows

---

## 🧠 Key Design Decisions

### Why Pre-Computed Forecasts?
The `production_forecast` table has quarterly forecasts pre-computed because:
- Genie SQL is best for querying, not statistical modeling
- Production forecasts depend on complex external factors (market trends, seasonal demand)
- The CEO question "expected production for Q3" should be instant, not wait for model training

### Why Mandatory Cooldown Business Rule?
Embedding the cooldown cycle in the data ensures Genie can answer "Why was production reduced?" with **actual reasons from the database**, not guessed correlations. The verified SQL explicitly joins to machine status logs.

### Why No Static Dashboard?
Because the contest theme is **"Genie at the Core."** A dashboard with 10 fixed charts would let users get insights without Genie — failing the gut check. TileGenie forces every insight through conversation.

---

## 🛡️ Troubleshooting

### "GENIE_SPACE_ID not found"
- Ensure the Genie Agent is added as a resource in `app.yaml`
- Check that the space ID is correctly formatted: `genie://<space-id>`

### "Query timed out"
- Your question might be too broad (e.g., asking for all data across 180 days)
- Try narrowing: "yesterday" instead of "this year", "Factory 1" instead of "all factories"

### "SQL errors in Genie responses"
- Go back to the Genie Agent configuration and test the question directly in the Genie UI
- Add it as a **verified answer** if it's a common question
- Refine the **instructions** to clarify the expected joins

### Data generation takes too long
- The script generates 180 days of history — reduce `DAYS_OF_HISTORY` to 90 or 60 in the script
- Or run it once and reuse the tables (no need to regenerate for every test)

---

## 📝 License

This project is built for the **Databricks Community Contest** and is provided as-is for educational and demonstration purposes.

---

## 🚀 Next Steps

1. **Generate the data** (Step 1)
2. **Create and test the Genie Agent** (Step 2)
3. **Deploy the app** (Steps 3-4)
4. **Create your demo video** showing the 4 core CEO questions working perfectly
5. **Write your Community Article** following the contest guidelines
6. **Submit your entry** before Aug 31, 2026

---

## 💬 Questions or Issues?

Reach out in the Databricks Community forum or reference the docs:
- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [Genie Agent Documentation](https://docs.databricks.com/en/genie/index.html)

---

**Built with ❤️ for the Databricks Community | Powered by Genie Agent**