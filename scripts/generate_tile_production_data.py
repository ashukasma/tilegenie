"""
TileGenie Synthetic Data Generator
Generates 16 Unity Catalog Delta tables for tile manufacturing demo
Catalog: tile_production_demo, Schema: gold
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random

# Import PySpark functions AFTER saving Python's built-in round
python_round = round  # Save Python's round before it gets shadowed
from pyspark.sql.functions import *
round = python_round  # Restore Python's round

# Initialize Spark
spark = SparkSession.builder.appName("TileGenie_DataGen").getOrCreate()

# Configuration
CATALOG = "tile_production_demo"
SCHEMA = "gold"
NUM_FACTORIES = 3
NUM_WAREHOUSES = 5
NUM_PRODUCTS = 12
NUM_CUSTOMERS = 50
NUM_SALES_REPS = 8
NUM_EVENTS = 6
DAYS_OF_HISTORY = 180  # 6 months

# Create catalog and schema
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
spark.sql(f"USE SCHEMA {SCHEMA}")

print(f"Generating data into {CATALOG}.{SCHEMA}...")

# ============================================================================
# DIMENSION TABLES
# ============================================================================

# 1. dim_warehouse
warehouse_data = [
    (1, "Mumbai Central", "Mumbai", "Maharashtra", "West", 50000, "2020-01-15"),
    (2, "Delhi North", "Delhi", "Delhi", "North", 40000, "2019-06-10"),
    (3, "Bangalore Tech Park", "Bangalore", "Karnataka", "South", 35000, "2021-03-20"),
    (4, "Hyderabad Hub", "Hyderabad", "Telangana", "South", 30000, "2020-11-05"),
    (5, "Pune Industrial", "Pune", "Maharashtra", "West", 25000, "2022-02-18")
]

dim_warehouse = spark.createDataFrame(warehouse_data, 
    ["warehouse_id", "warehouse_name", "city", "state", "region", "capacity_sqft", "opened_date"])

dim_warehouse.write.format("delta").mode("overwrite").saveAsTable("dim_warehouse")
print("✓ Created dim_warehouse")

# 2. dim_factory
factory_data = [
    (1, "Morbi Ceramics Plant", "Morbi", "Gujarat", "West", 15000, "2018-01-10"),
    (2, "Rajasthan Tiles Factory", "Jaipur", "Rajasthan", "North", 12000, "2019-05-15"),
    (3, "Tamil Nadu Production Unit", "Chennai", "Tamil Nadu", "South", 10000, "2020-08-20")
]

dim_factory = spark.createDataFrame(factory_data,
    ["factory_id", "factory_name", "city", "state", "region", "production_capacity_units_per_day", "commissioned_date"])

dim_factory.write.format("delta").mode("overwrite").saveAsTable("dim_factory")
print("✓ Created dim_factory")

# 3. dim_machine (with mandatory cooldown rules)
machine_types = ["Hydraulic Press", "Kiln", "Glazing Line", "Cutting Machine", "Polishing Unit"]
machines = []
machine_id = 1

for factory_id in range(1, NUM_FACTORIES + 1):
    # Each factory has 4-6 machines of different types
    num_machines = random.randint(4, 6)
    for i in range(num_machines):
        machine_type = random.choice(machine_types)
        # Key business rule: max continuous run and mandatory cooldown
        max_run = random.choice([8, 12, 16, 20])  # hours
        cooldown = random.choice([2, 3, 4])  # hours
        installed = (datetime.now() - timedelta(days=random.randint(365, 1500))).strftime("%Y-%m-%d")
        
        machines.append((
            machine_id,
            factory_id,
            f"{machine_type}-{factory_id}-{i+1}",
            machine_type,
            random.choice(["Installed", "Installed", "Installed", "Under Maintenance"]),
            max_run,
            cooldown,
            installed
        ))
        machine_id += 1

dim_machine = spark.createDataFrame(machines,
    ["machine_id", "factory_id", "machine_name", "machine_type", "status", 
     "max_continuous_run_hours", "mandatory_cooldown_hours", "installation_date"])

dim_machine.write.format("delta").mode("overwrite").saveAsTable("dim_machine")
print("✓ Created dim_machine")

# 4. dim_product
tile_types = ["Porcelain", "Ceramic", "Vitrified", "Mosaic"]
finishes = ["Glossy", "Matte", "Rustic"]
products = []

for i in range(1, NUM_PRODUCTS + 1):
    tile_type = random.choice(tile_types)
    finish = random.choice(finishes)
    size = random.choice(["12x12", "16x16", "24x24", "12x24"])
    price = round(random.uniform(25, 150), 2)
    
    products.append((
        i,
        f"{tile_type}-{finish}-{size}",
        tile_type,
        finish,
        size,
        price,
        random.randint(50, 200),
        random.randint(1000, 5000)
    ))

dim_product = spark.createDataFrame(products,
    ["product_id", "product_name", "tile_type", "finish", "size", "price_per_sqft",
     "production_time_minutes", "reorder_point"])

dim_product.write.format("delta").mode("overwrite").saveAsTable("dim_product")
print("✓ Created dim_product")

# 5. dim_customer
customer_types = ["Dealer", "Builder", "Retailer", "Direct"]
customers = []

for i in range(1, NUM_CUSTOMERS + 1):
    ctype = random.choice(customer_types)
    customers.append((
        i,
        f"Customer_{i}",
        ctype,
        random.choice(["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Chennai", "Kolkata"]),
        random.choice(["Maharashtra", "Delhi", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal"]),
        random.choice(["Active", "Active", "Active", "Inactive"]),
        (datetime.now() - timedelta(days=random.randint(30, 1000))).strftime("%Y-%m-%d")
    ))

dim_customer = spark.createDataFrame(customers,
    ["customer_id", "customer_name", "customer_type", "city", "state", "status", "onboarded_date"])

dim_customer.write.format("delta").mode("overwrite").saveAsTable("dim_customer")
print("✓ Created dim_customer")

# 6. dim_event (trade shows, exhibitions)
events = [
    (1, "India Ceramic & Tiles Expo 2026", "Mumbai", "2026-03-15", "2026-03-18", 5000),
    (2, "BuildTech Asia", "Bangalore", "2026-05-10", "2026-05-12", 3000),
    (3, "Infrastructure Summit", "Delhi", "2026-07-20", "2026-07-22", 4000),
    (4, "Gujarat Tiles Fair", "Ahmedabad", "2026-09-05", "2026-09-07", 2500),
    (5, "South India Construction Expo", "Chennai", "2026-11-12", "2026-11-14", 3500),
    (6, "National Building Materials Show", "Hyderabad", "2026-12-08", "2026-12-10", 4500)
]

dim_event = spark.createDataFrame(events,
    ["event_id", "event_name", "location", "start_date", "end_date", "expected_footfall"])

dim_event.write.format("delta").mode("overwrite").saveAsTable("dim_event")
print("✓ Created dim_event")

# 7. dim_sales_rep
reps = []
for i in range(1, NUM_SALES_REPS + 1):
    reps.append((
        i,
        f"Rep_{i}",
        f"rep{i}@tilegenie.com",
        random.choice(["North", "South", "East", "West"]),
        (datetime.now() - timedelta(days=random.randint(180, 1500))).strftime("%Y-%m-%d")
    ))

dim_sales_rep = spark.createDataFrame(reps,
    ["sales_rep_id", "rep_name", "email", "territory", "hire_date"])

dim_sales_rep.write.format("delta").mode("overwrite").saveAsTable("dim_sales_rep")
print("✓ Created dim_sales_rep")

# ============================================================================
# FACT TABLES - IoT/Machine
# ============================================================================

# Get machine list for fact generation
machines_df = spark.table("dim_machine").collect()

# 8. fact_machine_status_log
# Implements the mandatory cooldown business rule
status_log = []
log_id = 1

for machine_row in machines_df:
    machine_id = machine_row['machine_id']
    max_run = machine_row['max_continuous_run_hours']
    cooldown = machine_row['mandatory_cooldown_hours']
    
    # Generate status logs for last 180 days
    current_date = datetime.now() - timedelta(days=DAYS_OF_HISTORY)
    end_date = datetime.now()
    
    while current_date < end_date:
        # Running phase
        run_hours = random.randint(int(max_run * 0.7), max_run)  # Run 70-100% of max
        status_log.append((
            log_id,
            machine_id,
            current_date.strftime("%Y-%m-%d %H:%M:%S"),
            (current_date + timedelta(hours=run_hours)).strftime("%Y-%m-%d %H:%M:%S"),
            "Running",
            None
        ))
        log_id += 1
        current_date += timedelta(hours=run_hours)
        
        # Scheduled cooldown phase (mandatory)
        status_log.append((
            log_id,
            machine_id,
            current_date.strftime("%Y-%m-%d %H:%M:%S"),
            (current_date + timedelta(hours=cooldown)).strftime("%Y-%m-%d %H:%M:%S"),
            "Scheduled Cooldown",
            "Mandatory maintenance cycle"
        ))
        log_id += 1
        current_date += timedelta(hours=cooldown)
        
        # Occasional breakdowns (10% chance)
        if random.random() < 0.10:
            breakdown_hours = random.randint(4, 24)
            status_log.append((
                log_id,
                machine_id,
                current_date.strftime("%Y-%m-%d %H:%M:%S"),
                (current_date + timedelta(hours=breakdown_hours)).strftime("%Y-%m-%d %H:%M:%S"),
                "Breakdown",
                random.choice(["Bearing failure", "Hydraulic leak", "Electrical fault", "Overheating"])
            ))
            log_id += 1
            current_date += timedelta(hours=breakdown_hours)
        
        # Occasional idle periods when no orders (5% chance)
        if random.random() < 0.05:
            idle_hours = random.randint(8, 48)
            status_log.append((
                log_id,
                machine_id,
                current_date.strftime("%Y-%m-%d %H:%M:%S"),
                (current_date + timedelta(hours=idle_hours)).strftime("%Y-%m-%d %H:%M:%S"),
                "Idle",
                "No production orders"
            ))
            log_id += 1
            current_date += timedelta(hours=idle_hours)

fact_machine_status_log = spark.createDataFrame(status_log,
    ["log_id", "machine_id", "start_time", "end_time", "status", "reason"])

fact_machine_status_log.write.format("delta").mode("overwrite").saveAsTable("fact_machine_status_log")
print("✓ Created fact_machine_status_log")

# 9. fact_machine_sensor_reading
sensor_readings = []
reading_id = 1

for machine_row in machines_df:
    machine_id = machine_row['machine_id']
    
    # Generate hourly sensor readings for last 30 days
    current_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    while current_date < end_date:
        sensor_readings.append((
            reading_id,
            machine_id,
            current_date.strftime("%Y-%m-%d %H:%M:%S"),
            round(random.uniform(60, 95), 1),  # temperature
            round(random.uniform(30, 60), 1),  # vibration
            round(random.uniform(80, 150), 1),  # power_consumption
            round(random.uniform(40, 70), 1)   # humidity
        ))
        reading_id += 1
        current_date += timedelta(hours=1)

fact_machine_sensor_reading = spark.createDataFrame(sensor_readings,
    ["reading_id", "machine_id", "timestamp", "temperature_celsius", 
     "vibration_hz", "power_consumption_kwh", "humidity_percent"])

fact_machine_sensor_reading.write.format("delta").mode("overwrite").saveAsTable("fact_machine_sensor_reading")
print("✓ Created fact_machine_sensor_reading")

# ============================================================================
# FACT TABLES - Production
# ============================================================================

# 10. fact_production_daily
production_daily = []

for factory_id in range(1, NUM_FACTORIES + 1):
    for days_back in range(DAYS_OF_HISTORY):
        prod_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        for product_id in random.sample(range(1, NUM_PRODUCTS + 1), random.randint(3, 6)):
            planned = random.randint(500, 2000)
            
            # Actual production influenced by machine downtime
            efficiency = random.uniform(0.75, 0.98)  # 75-98% efficiency
            actual = int(planned * efficiency)
            defects = int(actual * random.uniform(0.01, 0.05))  # 1-5% defect rate
            downtime_minutes = random.randint(0, 240)  # 0-4 hours downtime
            
            production_daily.append((
                factory_id,
                product_id,
                prod_date,
                planned,
                actual,
                defects,
                downtime_minutes,
                round(random.uniform(85, 99), 2)  # efficiency %
            ))

fact_production_daily = spark.createDataFrame(production_daily,
    ["factory_id", "product_id", "production_date", "planned_units", 
     "actual_units", "defect_units", "downtime_minutes", "efficiency_percent"])

fact_production_daily.write.format("delta").mode("overwrite").saveAsTable("fact_production_daily")
print("✓ Created fact_production_daily")

# 11. production_forecast
# Pre-computed quarterly forecast (Genie queries this, doesn't forecast live)
forecast_data = []

for product_id in range(1, NUM_PRODUCTS + 1):
    base_production = random.randint(50000, 200000)
    
    for quarter_offset in range(0, 5):  # Next 5 quarters
        year = 2026 + (quarter_offset // 4)
        quarter = (quarter_offset % 4) + 1
        
        # Add seasonal variation and growth trend
        seasonal_factor = random.uniform(0.9, 1.15)
        growth_factor = 1 + (quarter_offset * 0.03)  # 3% quarterly growth
        
        forecast_units = int(base_production * seasonal_factor * growth_factor)
        lower_bound = int(forecast_units * 0.85)
        upper_bound = int(forecast_units * 1.15)
        
        forecast_data.append((
            product_id,
            year,
            quarter,
            forecast_units,
            lower_bound,
            upper_bound,
            round(random.uniform(0.75, 0.95), 2)  # confidence
        ))

production_forecast = spark.createDataFrame(forecast_data,
    ["product_id", "year", "quarter", "forecast_units", 
     "lower_bound", "upper_bound", "confidence_level"])

production_forecast.write.format("delta").mode("overwrite").saveAsTable("production_forecast")
print("✓ Created production_forecast")

# ============================================================================
# FACT TABLES - Inventory/Warehouse
# ============================================================================

# 12. fact_inventory_snapshot
inventory_snapshots = []

for warehouse_id in range(1, NUM_WAREHOUSES + 1):
    for days_back in range(0, DAYS_OF_HISTORY, 7):  # Weekly snapshots
        snapshot_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        for product_id in range(1, NUM_PRODUCTS + 1):
            stock = random.randint(500, 5000)
            reorder = random.randint(1000, 3000)
            
            inventory_snapshots.append((
                warehouse_id,
                product_id,
                snapshot_date,
                stock,
                reorder,
                "Low" if stock < reorder else "Adequate"
            ))

fact_inventory_snapshot = spark.createDataFrame(inventory_snapshots,
    ["warehouse_id", "product_id", "snapshot_date", 
     "stock_quantity", "reorder_point", "stock_status"])

fact_inventory_snapshot.write.format("delta").mode("overwrite").saveAsTable("fact_inventory_snapshot")
print("✓ Created fact_inventory_snapshot")

# 13. fact_stock_transfer
stock_transfers = []
transfer_id = 1

for _ in range(500):  # 500 transfers
    from_warehouse = random.randint(1, NUM_WAREHOUSES)
    to_warehouse = random.choice([w for w in range(1, NUM_WAREHOUSES + 1) if w != from_warehouse])
    
    transfer_date = (datetime.now() - timedelta(days=random.randint(0, DAYS_OF_HISTORY))).strftime("%Y-%m-%d")
    product_id = random.randint(1, NUM_PRODUCTS)
    quantity = random.randint(100, 1000)
    
    stock_transfers.append((
        transfer_id,
        from_warehouse,
        to_warehouse,
        product_id,
        transfer_date,
        quantity,
        random.choice(["Completed", "Completed", "Completed", "In Transit"])
    ))
    transfer_id += 1

fact_stock_transfer = spark.createDataFrame(stock_transfers,
    ["transfer_id", "from_warehouse_id", "to_warehouse_id", "product_id",
     "transfer_date", "quantity", "status"])

fact_stock_transfer.write.format("delta").mode("overwrite").saveAsTable("fact_stock_transfer")
print("✓ Created fact_stock_transfer")

# ============================================================================
# FACT TABLES - CRM/Sales
# ============================================================================

# 14. fact_crm_interaction
interaction_types = ["Call", "Email", "Meeting", "Demo", "Quote"]
interactions = []
interaction_id = 1

for _ in range(1000):  # 1000 CRM interactions
    customer_id = random.randint(1, NUM_CUSTOMERS)
    rep_id = random.randint(1, NUM_SALES_REPS)
    interaction_date = (datetime.now() - timedelta(days=random.randint(0, DAYS_OF_HISTORY))).strftime("%Y-%m-%d")
    
    interactions.append((
        interaction_id,
        customer_id,
        rep_id,
        interaction_date,
        random.choice(interaction_types),
        random.choice(["Positive", "Neutral", "Follow-up Needed"]),
        random.choice([None, 1, 2, 3, 4, 5, 6])  # event_id if event-related
    ))
    interaction_id += 1

fact_crm_interaction = spark.createDataFrame(interactions,
    ["interaction_id", "customer_id", "sales_rep_id", "interaction_date",
     "interaction_type", "outcome", "event_id"])

fact_crm_interaction.write.format("delta").mode("overwrite").saveAsTable("fact_crm_interaction")
print("✓ Created fact_crm_interaction")

# 15. fact_orders
orders = []
order_id = 1

for _ in range(800):  # 800 orders
    customer_id = random.randint(1, NUM_CUSTOMERS)
    rep_id = random.randint(1, NUM_SALES_REPS)
    order_date = (datetime.now() - timedelta(days=random.randint(0, DAYS_OF_HISTORY))).strftime("%Y-%m-%d")
    
    quantity = random.randint(100, 5000)
    product_id = random.randint(1, NUM_PRODUCTS)
    unit_price = round(random.uniform(25, 150), 2)
    total_value = round(quantity * unit_price, 2)
    
    orders.append((
        order_id,
        customer_id,
        rep_id,
        product_id,
        order_date,
        quantity,
        unit_price,
        total_value,
        random.choice(["Delivered", "Delivered", "Delivered", "In Production", "Pending"]),
        random.choice([None, 1, 2, 3, 4, 5, 6])  # event_id if from event
    ))
    order_id += 1

fact_orders = spark.createDataFrame(orders,
    ["order_id", "customer_id", "sales_rep_id", "product_id", "order_date",
     "quantity", "unit_price", "total_value", "status", "event_id"])

fact_orders.write.format("delta").mode("overwrite").saveAsTable("fact_orders")
print("✓ Created fact_orders")

# 16. fact_event_attendance
attendance = []
attendance_id = 1

for event_id in range(1, NUM_EVENTS + 1):
    # Random subset of customers attend each event
    num_attendees = random.randint(15, 35)
    attending_customers = random.sample(range(1, NUM_CUSTOMERS + 1), num_attendees)
    
    for customer_id in attending_customers:
        attendance.append((
            attendance_id,
            event_id,
            customer_id,
            random.choice(["Registered", "Attended", "No-show"]),
            random.randint(1, 10)  # interest_score 1-10
        ))
        attendance_id += 1

fact_event_attendance = spark.createDataFrame(attendance,
    ["attendance_id", "event_id", "customer_id", "attendance_status", "interest_score"])

fact_event_attendance.write.format("delta").mode("overwrite").saveAsTable("fact_event_attendance")
print("✓ Created fact_event_attendance")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("✅ DATA GENERATION COMPLETE")
print("="*70)
print(f"Catalog: {CATALOG}")
print(f"Schema: {SCHEMA}")
print(f"Tables created: 16")
print(f"Days of history: {DAYS_OF_HISTORY}")
print("\nDimension Tables (7):")
print("  - dim_warehouse, dim_factory, dim_machine, dim_product")
print("  - dim_customer, dim_event, dim_sales_rep")
print("\nFact Tables (9):")
print("  IoT/Machine: fact_machine_status_log, fact_machine_sensor_reading")
print("  Production: fact_production_daily, production_forecast")
print("  Inventory: fact_inventory_snapshot, fact_stock_transfer")
print("  CRM/Sales: fact_crm_interaction, fact_orders, fact_event_attendance")
print("\n🔑 Key Business Rules Embedded:")
print("  - Machines have max_continuous_run_hours and mandatory_cooldown_hours")
print("  - Status logs show Running → Scheduled Cooldown cycles")
print("  - Occasional Breakdowns and Idle periods with reason codes")
print("  - Production forecast pre-computed quarterly (don't forecast live)")
print("="*70)