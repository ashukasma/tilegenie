# TileGenie - Genie Agent Configuration Guide

This document provides the complete configuration for setting up the Genie Agent that powers TileGenie.

---

## 1. Genie Agent Instructions

Copy the following text into the **Instructions** field when creating your Genie Agent:

```
You are TileGenie, an AI assistant for a tile manufacturing company. You help leadership answer operational questions about production, inventory, sales, and machine performance.

## Data Model
You have access to 16 Delta tables in catalog `tile_production_demo`, schema `gold`:

**Dimensions:**
- dim_warehouse: Warehouse locations, capacity
- dim_factory: Factory locations, production capacity
- dim_machine: Machines with max_continuous_run_hours and mandatory_cooldown_hours
- dim_product: Tile products with pricing, production time
- dim_customer: Customer details, types (Dealer/Builder/Retailer/Direct)
- dim_event: Trade shows and exhibitions
- dim_sales_rep: Sales representatives and territories

**IoT/Machine Facts:**
- fact_machine_status_log: Machine status over time (Running, Scheduled Cooldown, Breakdown, Idle) with reason codes
- fact_machine_sensor_reading: Hourly sensor data (temperature, vibration, power, humidity)

**Production Facts:**
- fact_production_daily: Daily production by factory and product (planned vs actual vs defects vs downtime)
- production_forecast: Pre-computed quarterly forecasts with confidence bounds

**Inventory Facts:**
- fact_inventory_snapshot: Weekly warehouse stock levels by product
- fact_stock_transfer: Inter-warehouse transfers

**CRM/Sales Facts:**
- fact_crm_interaction: Customer interactions by sales reps
- fact_orders: Orders with status and values
- fact_event_attendance: Customer attendance and interest at trade shows

## Key Business Rules

### Production Reduction Analysis
When asked "Why was production reduced on [date/factory]?", you must:
1. Join fact_production_daily to fact_machine_status_log on machine_id and date
2. Look for machines in "Breakdown" or "Scheduled Cooldown" or "Idle" status
3. Sum downtime_minutes from fact_production_daily
4. Join to dim_machine to get machine names and cooldown rules
5. Provide specific reasons from the status log (e.g., "Bearing failure", "Mandatory maintenance cycle", "No production orders")

NEVER guess or infer reasons - always query the actual status logs.

### Production Forecasting
When asked about "expected production" or "production plan":
- Query the production_forecast table which has pre-computed quarterly forecasts
- DO NOT attempt to compute forecasts yourself using statistical functions
- The forecast includes forecast_units, lower_bound, upper_bound, and confidence_level
- Join to dim_product for product details

### Inventory Queries
When asked "How much stock do we have in each warehouse?":
- Query fact_inventory_snapshot with the LATEST snapshot_date
- Use: `WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM fact_inventory_snapshot)`
- Join to dim_warehouse for warehouse names and dim_product for product names
- Show stock_status (Low/Adequate) and compare to reorder_point

### Machine Cooldown Cycles
All machines have:
- max_continuous_run_hours: Maximum hours before mandatory cooldown
- mandatory_cooldown_hours: Required downtime for maintenance

Machines cycle: Running → Scheduled Cooldown → Running
Occasional Breakdowns and Idle periods interrupt the cycle.

## Answer Style
- Be concise and executive-friendly
- Lead with the answer, then supporting data
- Use specific numbers and dates
- When showing production drops, ALWAYS cite the actual machine status reasons from the database
- Format large numbers with commas (e.g., 1,234,567)
```

---

## 2. Sample Questions (8-10)

Add these to the **Sample Questions** section in Genie Agent:

1. **Why was production reduced yesterday?**
2. **What is the expected production of Porcelain-Glossy-24x24 for next quarter?**
3. **What should our production plan be for Q3 2026?**
4. **How much stock do we have in each warehouse right now?**
5. **Which machines had the most downtime this month?**
6. **What is the defect rate trend across our factories?**
7. **Which products have low stock levels?**
8. **How many orders came from the Mumbai Ceramics Expo?**
9. **What is the average machine efficiency by factory?**
10. **Which customers placed the largest orders this quarter?**

---

## 3. Verified Answers (4 Core CEO Questions)

These are the **exact SQL queries** Genie should generate for the 4 critical CEO questions. Add these as **Verified Answers** in the Genie Agent:

### Question 1: "Why was production reduced on 2026-08-20 at Factory 1?"

**Expected SQL:**
```sql
SELECT 
  pd.production_date,
  pd.factory_id,
  f.factory_name,
  pd.product_id,
  p.product_name,
  pd.planned_units,
  pd.actual_units,
  pd.planned_units - pd.actual_units AS shortfall,
  pd.downtime_minutes,
  pd.efficiency_percent,
  ms.status AS machine_status,
  ms.reason AS downtime_reason,
  m.machine_name,
  m.machine_type
FROM tile_production_demo.gold.fact_production_daily pd
INNER JOIN tile_production_demo.gold.dim_factory f ON pd.factory_id = f.factory_id
INNER JOIN tile_production_demo.gold.dim_product p ON pd.product_id = p.product_id
LEFT JOIN tile_production_demo.gold.dim_machine m ON m.factory_id = pd.factory_id
LEFT JOIN tile_production_demo.gold.fact_machine_status_log ms 
  ON ms.machine_id = m.machine_id 
  AND DATE(ms.start_time) = pd.production_date
  AND ms.status IN ('Breakdown', 'Scheduled Cooldown', 'Idle')
WHERE pd.production_date = '2026-08-20'
  AND pd.factory_id = 1
  AND pd.actual_units < pd.planned_units
ORDER BY shortfall DESC
```

**Expected Answer Structure:**
"Production was reduced at Factory 1 on 2026-08-20 due to:
- [Product Name]: [X] units short of plan ([Y]% efficiency)
  - Cause: [Machine Type] was in [Status] - [Reason]
  - Total downtime: [Z] minutes"

---

### Question 2: "What is the expected production of Porcelain-Glossy-24x24 for next quarter?"

**Expected SQL:**
```sql
SELECT 
  p.product_name,
  pf.year,
  pf.quarter,
  pf.forecast_units,
  pf.lower_bound,
  pf.upper_bound,
  pf.confidence_level,
  CONCAT(
    FORMAT_NUMBER(pf.forecast_units, 0), 
    ' units (', 
    FORMAT_NUMBER(pf.lower_bound, 0), 
    ' - ', 
    FORMAT_NUMBER(pf.upper_bound, 0), 
    ')'
  ) AS forecast_range
FROM tile_production_demo.gold.production_forecast pf
INNER JOIN tile_production_demo.gold.dim_product p ON pf.product_id = p.product_id
WHERE p.product_name = 'Porcelain-Glossy-24x24'
  AND pf.year = YEAR(ADD_MONTHS(CURRENT_DATE(), 3))
  AND pf.quarter = QUARTER(ADD_MONTHS(CURRENT_DATE(), 3))
```

**Expected Answer Structure:**
"Expected production for Porcelain-Glossy-24x24 in Q[X] [YEAR]:
- Forecast: [X,XXX] units
- Range: [Lower] - [Upper] units
- Confidence: [XX]%"

---

### Question 3: "What should our production plan be for all products in Q4 2026?"

**Expected SQL:**
```sql
SELECT 
  p.product_name,
  p.tile_type,
  pf.forecast_units,
  pf.lower_bound,
  pf.upper_bound,
  pf.confidence_level,
  p.price_per_sqft,
  ROUND(pf.forecast_units * p.price_per_sqft, 2) AS projected_revenue
FROM tile_production_demo.gold.production_forecast pf
INNER JOIN tile_production_demo.gold.dim_product p ON pf.product_id = p.product_id
WHERE pf.year = 2026
  AND pf.quarter = 4
ORDER BY projected_revenue DESC
```

**Expected Answer Structure:**
"Production plan for Q4 2026:

Top products by projected revenue:
1. [Product]: [X,XXX] units → $[Y,YYY] revenue (confidence: [Z]%)
2. [Product]: [X,XXX] units → $[Y,YYY] revenue (confidence: [Z]%)
...

Total forecasted units: [Sum]
Total projected revenue: $[Sum]"

---

### Question 4: "How much stock do we have in each warehouse?"

**Expected SQL:**
```sql
WITH latest_snapshot AS (
  SELECT MAX(snapshot_date) AS max_date
  FROM tile_production_demo.gold.fact_inventory_snapshot
)
SELECT 
  w.warehouse_name,
  w.city,
  w.region,
  p.product_name,
  inv.stock_quantity,
  inv.reorder_point,
  inv.stock_status,
  CASE 
    WHEN inv.stock_quantity < inv.reorder_point THEN 'REORDER NEEDED'
    ELSE 'Adequate'
  END AS action_needed
FROM tile_production_demo.gold.fact_inventory_snapshot inv
INNER JOIN tile_production_demo.gold.dim_warehouse w ON inv.warehouse_id = w.warehouse_id
INNER JOIN tile_production_demo.gold.dim_product p ON inv.product_id = p.product_id
CROSS JOIN latest_snapshot ls
WHERE inv.snapshot_date = ls.max_date
ORDER BY w.warehouse_name, inv.stock_status, inv.stock_quantity
```

**Expected Answer Structure:**
"Current warehouse stock (as of [date]):

**Mumbai Central:**
- [Product]: [X,XXX] units ([Status])
- [Product]: [X,XXX] units (REORDER NEEDED)
...

**Delhi North:**
- [Product]: [X,XXX] units ([Status])
...

⚠️ Low stock alerts: [Count] products need reordering"

---

## 4. Tables to Add to Genie Space

When creating the Genie Space, add all 16 tables from `tile_production_demo.gold`:

**Dimensions (7):**
1. `tile_production_demo.gold.dim_warehouse`
2. `tile_production_demo.gold.dim_factory`
3. `tile_production_demo.gold.dim_machine`
4. `tile_production_demo.gold.dim_product`
5. `tile_production_demo.gold.dim_customer`
6. `tile_production_demo.gold.dim_event`
7. `tile_production_demo.gold.dim_sales_rep`

**Facts (9):**
8. `tile_production_demo.gold.fact_machine_status_log`
9. `tile_production_demo.gold.fact_machine_sensor_reading`
10. `tile_production_demo.gold.fact_production_daily`
11. `tile_production_demo.gold.production_forecast`
12. `tile_production_demo.gold.fact_inventory_snapshot`
13. `tile_production_demo.gold.fact_stock_transfer`
14. `tile_production_demo.gold.fact_crm_interaction`
15. `tile_production_demo.gold.fact_orders`
16. `tile_production_demo.gold.fact_event_attendance`

---

## 5. Setup Checklist

- [ ] Run `generate_tile_production_data.py` to create all 16 tables
- [ ] Create a new Genie Space named "TileGenie Production Intelligence"
- [ ] Add all 16 tables to the Genie Space
- [ ] Copy the Instructions text into the Genie Agent instructions field
- [ ] Add all 10 sample questions
- [ ] Add all 4 verified answers with SQL
- [ ] Test each of the 4 core CEO questions and verify the SQL matches
- [ ] Note the Genie Space ID (you'll need it for `app.yaml`)

---

## 6. Testing the Genie Agent

Before integrating with the app, test these questions directly in the Genie UI:

✅ **Must work perfectly (contest demo questions):**
1. "Why was production reduced on [recent date] at Factory 1?"
2. "What is the expected production of [any product] for next quarter?"
3. "What should our production plan be for Q4 2026?"
4. "How much stock do we have in each warehouse?"

✅ **Should work well (stretch goals):**
5. "Which machines had the most downtime this week?"
6. "What is our defect rate by product type?"
7. "Which products are low in stock?"
8. "Show me orders from the Mumbai expo"

If any of the 4 core questions don't return the expected SQL structure, refine the Genie instructions or add more verified answers.

---

**Next Step:** Once the Genie Agent is configured and tested, proceed to building the Streamlit app (`app.py`).