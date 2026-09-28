import mysql.connector

connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = os.getenv("MYSQL_PASSWORD"),
    database = "production_maintenance_db"
)

if connection.is_connected():
    print("MySQL Database Connected Successfully!")


import pandas as pd

departments_df = pd.read_sql("SELECT * FROM departments", connection)
machines_df = pd.read_sql("SELECT * FROM machines", connection)
products_df = pd.read_sql("SELECT * FROM products", connection)
shifts_df = pd.read_sql("SELECT * FROM shifts", connection)
production_df = pd.read_sql("SELECT * FROM production_records", connection)
breakdowns_df = pd.read_sql("SELECT * FROM breakdowns", connection)
maintenance_df = pd.read_sql("SELECT * FROM maintenance_record", connection)
schedule_df = pd.read_sql("SELECT * FROM machine_schedule", connection)
quality_df = pd.read_sql("SELECT * FROM quality_records", connection)


production_df["efficiency_percentage"]= ((production_df)["actual_qty"]/production_df["target_qty"])*100

production_df["efficiency_percentage"] = production_df["efficiency_percentage"].round(2)

print("\nProduction Efficiency :")

print(production_df[["production_id","target_qty","actual_qty","efficiency_percentage"]])


#rejection percentage

production_df["rejection_percentage"] = (production_df["rejected_qty"]/production_df["actual_qty"] ) *100
production_df["rejection_percentage"] = (production_df["rejection_percentage"].round(2))

print("\nRejection Percentage:")

print(
    production_df[
        ["production_id", "actual_qty", "rejected_qty", "rejection_percentage"]
    ]
)


#Good Quality Percentage

production_df["good_quality_percentage"] = (
    production_df["good_qty"] / production_df["actual_qty"]
) * 100

production_df["good_quality_percentage"] = (
    production_df["good_quality_percentage"].round(2)
)

print("\nGood Quality Percentage:")

print(
    production_df[
        [
            "production_id",
            "actual_qty",
            "good_qty",
            "good_quality_percentage"
        ]
    ]
)

# Production Gap

production_df["production_gap"] = (
    production_df["target_qty"] - production_df["actual_qty"]
)

print("\nProduction Gap:")

print(
    production_df[
        ["production_id", "target_qty", "actual_qty", "production_gap"]
    ]
)


total_target = production_df["target_qty"].sum()
total_actual = production_df["actual_qty"].sum()
total_good = production_df["good_qty"].sum()
total_rejection = production_df["rejected_qty"].sum()

overall_efficiency = (total_actual/total_target)*100
overall_rejection = (total_rejection / total_actual) * 100
overall_good_quality = (total_good/total_actual)*100

print("\nOverall Production Summary:")

print("Total Target:", total_target)
print("Total Actual:", total_actual)
print("Total Good:", total_good)
print("Total Rejected:", total_rejection)
print("Overall Efficiency:", round(overall_efficiency, 2), "%")
print("Overall Rejection:", round(overall_rejection, 2), "%")
print("Overall Good Quality:", round(overall_good_quality, 2), "%")


# Machine-wise Performance Summary

machine_production_df = production_df.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)

print("\nMachine-wise Production:")

print(
    machine_production_df[
        [
            "production_id",
            "machine_id",
            "machine_name",
            "target_qty",
            "actual_qty",
            "good_qty",
            "rejected_qty"
        ]
    ]
)


# Machine-wise Summary

machine_summary = machine_production_df.groupby(
    ["machine_id", "machine_name"]
).agg(
    total_target=("target_qty", "sum"),
    total_actual=("actual_qty", "sum"),
    total_good=("good_qty", "sum"),
    total_rejection=("rejected_qty", "sum")
).reset_index()


print("\nMachine-wise Performance Summary:")

print(machine_summary)


# Machine-wise KPIs

machine_summary["efficiency_percentage"] = (
    machine_summary["total_actual"] /
    machine_summary["total_target"]
) * 100

machine_summary["rejection_percentage"] = (
    machine_summary["total_rejection"] /
    machine_summary["total_actual"]
) * 100

machine_summary["efficiency_percentage"] = (
    machine_summary["efficiency_percentage"].round(2)
)

machine_summary["rejection_percentage"] = (
    machine_summary["rejection_percentage"].round(2)
)


print("\nMachine-wise KPI Summary:")

print(
    machine_summary[
        [
            "machine_id",
            "machine_name",
            "total_target",
            "total_actual",
            "total_good",
            "total_rejection",
            "efficiency_percentage",
            "rejection_percentage"
        ]
    ]
)

print("\nBreakdown Records:")

print(
    breakdowns_df[
        [
            "breakdown_id",
            "machine_id",
            "breakdown_date",
            "breakdown_reason",
            "root_cause",
            "downtime_hours"
        ]
    ]
)

# Overall Breakdown Analysis

total_breakdowns = breakdowns_df["breakdown_id"].count()
total_downtime = breakdowns_df["downtime_hours"].sum()

print("\nOverall Breakdown Summary:")

print("Total Breakdowns:", total_breakdowns)
print("Total Downtime Hours:", total_downtime)

machine_downtime = breakdowns_df.groupby("machine_id").agg(
    total_breakdowns=("breakdown_id", "count"),
    total_downtime_hours=("downtime_hours", "sum")
).reset_index()

print("\nMachine-wise Downtime:")

print(machine_downtime)


machine_downtime = machine_downtime.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)

print("\nMachine-wise Downtime Analysis:")

print(
    machine_downtime[
        [
            "machine_id",
            "machine_name",
            "total_breakdowns",
            "total_downtime_hours"
        ]
    ]
)

highest_downtime_machine = machine_downtime.loc[
    machine_downtime["total_downtime_hours"].idxmax()
]

print("\nMachine with Highest Downtime:")

print("Machine:", highest_downtime_machine["machine_name"])
print("Downtime Hours:", highest_downtime_machine["total_downtime_hours"])
print("Breakdowns:", highest_downtime_machine["total_breakdowns"])

root_cause_summary = breakdowns_df.groupby("root_cause").agg(
    breakdown_count=("breakdown_id", "count"),
    total_downtime_hours=("downtime_hours", "sum")
).reset_index()

root_cause_summary = root_cause_summary.sort_values(
    "breakdown_count",
    ascending=False
)

print("\nRoot Cause Analysis:")
print(root_cause_summary)

machine_breakdown_df = breakdowns_df.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)

machine_breakdown_summary = machine_breakdown_df.groupby(
    ["machine_id", "machine_name"]
).agg(
    breakdown_count=("breakdown_id", "count"),
    total_downtime_hours=("downtime_hours", "sum")
).reset_index()

machine_breakdown_summary = machine_breakdown_summary.sort_values(
    "total_downtime_hours",
    ascending=False
)

print("\nMachine-wise Breakdown Summary:")
print(machine_breakdown_summary)

breakdown_reason_summary = breakdowns_df.groupby(
    "breakdown_reason"
).agg(
    breakdown_count=("breakdown_id", "count"),
    total_downtime_hours=("downtime_hours", "sum")
).reset_index()

breakdown_reason_summary = breakdown_reason_summary.sort_values(
    "total_downtime_hours",
    ascending=False
)

print("\nBreakdown Reason Summary:")
print(breakdown_reason_summary)

machine_breakdown_df = breakdowns_df.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)

machine_breakdown_summary = machine_breakdown_df.groupby(
    ["machine_id", "machine_name"]
).agg(
    breakdown_count=("breakdown_id", "count"),
    total_downtime_hours=("downtime_hours", "sum")
).reset_index()

machine_breakdown_summary = machine_breakdown_summary.sort_values(
    "total_downtime_hours",
    ascending=False
)

print("\nMachine-wise Breakdown Summary:")
print(machine_breakdown_summary)

#MAINTENANCE ANALYSIS

print("\nMaintenance Records: ")
print(
    maintenance_df[
        [
         "maintenance_id",
         "machine_id",
         "maintenance_type",
         "technician_name",
         "repair_hours",
         "maintenance_cost"
      ]
    ]
)

#Overall maintenance summery

total_maintenance_records = maintenance_df["maintenance_id"].count() 
total_repair_hours = maintenance_df["repair_hours"].sum()
total_maintenance_cost = maintenance_df["maintenance_cost"].sum()


print("\nOverall Maintenance Summary:")

print("Total Maintenance Records:", total_maintenance_records)

print("Total Repair Hours:", total_repair_hours)

print("Total Maintenance Cost:", total_maintenance_cost)


# Maintenance Type Analysis

maintenance_type_summary = maintenance_df.groupby(
    "maintenance_type"
).agg(
    maintenance_count=("maintenance_id", "count"),
    total_repair_hours=("repair_hours", "sum"),
    total_maintenance_cost=("maintenance_cost", "sum")
).reset_index()

print("\nMaintenance Type Summary:")

print(maintenance_type_summary)

# MACHINE-WISE MAINTENANCE ANALYSIS

machine_maintenance_df = maintenance_df.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)

machine_maintenance_summary = machine_maintenance_df.groupby(
    ["machine_id", "machine_name"]
).agg(
    maintenance_count=("maintenance_id", "count"),
    total_repair_hours=("repair_hours", "sum"),
    total_maintenance_cost=("maintenance_cost", "sum")
).reset_index()

machine_maintenance_summary = machine_maintenance_summary.sort_values(
    "total_maintenance_cost",
    ascending=False
)

print("\nMachine-wise Maintenance Summary:")

print(machine_maintenance_summary)

# MAINTENANCE SCHEDULE ANALYSIS

print("\nMaintenance Schedule:")
print(
    schedule_df[
        [
            "schedule_id",
            "machine_id",
            "maintenance_task",
            "frequency_days",
            "last_maintenance_date",
            "next_maintenance_date",
            "status"
        ]
    ]
)

#add machine name
machine_schedule_df = schedule_df.merge(
    machines_df[["machine_id", "machine_name"]],
    on="machine_id",
    how="left"
)


print("\nMachine-wise Maintenance Schedule:")

print(
    machine_schedule_df[
        [
            "schedule_id",
            "machine_id",
            "machine_name",
            "maintenance_task",
            "frequency_days",
            "last_maintenance_date",
            "next_maintenance_date",
            "status"
        ]
    ]
)

today = pd.Timestamp.today().normalize()

machine_schedule_df["next_maintenance_date"] = pd.to_datetime(machine_schedule_df["next_maintenance_date"])

machine_schedule_df["maintenance_status"] = machine_schedule_df["next_maintenance_date"].apply(
    lambda date:"overdue" if date< today else "Upcomping")

print("\nMaintenance Status:")

print(
    machine_schedule_df[
        [
            "machine_id",
            "machine_name",
            "maintenance_task",
            "next_maintenance_date",
            "maintenance_status"
        ]
    ]
)

#Quality analysis 

print("\nQuality Records:")
print(
    quality_df[
        [
            "quality_id",
            "production_id",
            "inspection_date",
            "good_qty",
            "rejection_reason"
        ]
    ]
)

#rejection reason analysis

quality_rejection_summary = quality_df.groupby(
    "rejection_reason"
).agg(
    inspection_count=("quality_id", "count"),
    total_good_qty=("good_qty", "sum")
).reset_index()

quality_rejection_summary = quality_rejection_summary.sort_values(
    "inspection_count",
    ascending=False
)

print("\nQuality Rejection Reason Summary:")

print(quality_rejection_summary)


#PRODUCTION-WISE QUALITY ANALYSIS

production_quality_df = production_df.merge(
    quality_df[
        [
            "production_id",
            "inspection_date",
            "good_qty",
            "rejection_reason"
        ]
    ],
    on="production_id",
    how="left",
    suffixes=("_production", "_quality")
)

print("\nProduction-wise Quality Analysis:")

print(
    production_quality_df[
        [
            "production_id",
            "actual_qty",
            "good_qty_production",
            "rejected_qty",
            "rejection_reason"
        ]
    ]
)

#quality KPI summery

quality_kpi_summary = production_quality_df.groupby(
    "rejection_reason"
).agg(
    total_production=("production_id", "count"),
    total_good_qty=("good_qty_production", "sum"),
    total_rejected_qty=("rejected_qty", "sum")
).reset_index()

quality_kpi_summary["rejection_percentage"] = (
    quality_kpi_summary["total_rejected_qty"] /
    (
        quality_kpi_summary["total_good_qty"] +
        quality_kpi_summary["total_rejected_qty"]
    )
) * 100

quality_kpi_summary["rejection_percentage"] = (
    quality_kpi_summary["rejection_percentage"].round(2)
)

print("\nQuality KPI Summary:")

print("\nQuality KPI Summary:")
print(quality_kpi_summary.head())

# NUMPY MACHINE-WISE PRODUCTION ANALYSIS

import numpy as np

machine_actual_qty = machine_production_df["actual_qty"].to_numpy()

print("\nMachine - wise Numpy Statistics: ")
print("Average Actual Production:",
      round(np.mean(machine_actual_qty), 2))

print("Median Actual Production:",
      round(np.median(machine_actual_qty), 2))

print("Production Variation:",
      round(np.std(machine_actual_qty), 2))

print("Lowest Actual Production:",
      np.min(machine_actual_qty))

print("Highest Actual Production:",
      np.max(machine_actual_qty))


# PLOTLY VISUALIZATION

import plotly.express as px

data = {
    "Machine": ["Hammer Mill", "Mixer", "Pellet Press", "Cooler"],
    "Production": [95, 110, 125, 118]
}

fig = px.bar(
    data,
    x= "Machine",
    y= "Production",
    title = "Machine - Wise Production"
)

import os

chart_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "production_target_vs_actual.html"
)

fig.write_html(chart_path)

print("Chart created at:", chart_path)


fig = px.bar(
    production_df,
    x = "production_id",
    y=["target_qty","actual_qty"],
    title = "Production target vs Actual",
    labels ={
          "production_id": "Production ID",
        "value": "Quantity (MT)",
        "variable": "Production"
    },
    barmode = "group"

)

fig.write_html("production_target_vs_actual.html")

print("\nProduction Target vs Actual chart created successfully!")


fix = px.bar(
    machine_summary,
    x="machine_name",
    y="efficiency_percentage",
    title="Machine-wise Production Efficiency",
    labels={
        "machine_name": "Machine",
        "efficiency_percentage": "Efficiency (%)"
    }
)

fig.write_html("machine_wise_efficiency.html")

print("Machine-wise efficiency chart created successfully!")


# MACHINE-WISE DOWNTIME CHART
fig = px.bar(
    machine_downtime,
    x="machine_name",
    y="total_downtime_hours",
    title="Machine-wise Total Downtime",
    labels={
        "machine_name": "Machine",
        "total_downtime_hours": "Downtime (Hours)"
    }
)

fig.write_html("machine_wise_downtime.html")

print("Machine-wise downtime chart created successfully!")

# BREAKDOWN REASON ANALYSIS

fig = px.bar(
    breakdown_reason_summary,
    x="breakdown_reason",
    y="total_downtime_hours",
    title="Breakdown Reason-wise Downtime",
    labels={
        "breakdown_reason": "Breakdown Reason",
        "total_downtime_hours": "Downtime (Hours)"
    }
)

fig.write_html("breakdown_reason_downtime.html")

print("Breakdown reason chart created successfully!")

# QUALITY REJECTION ANALYSIS

fig = px.bar(
    quality_rejection_summary,
    x="rejection_reason",
    y="inspection_count",
    title="Rejection Reason-wise Inspection Count",
    labels={
        "rejection_reason": "Rejection Reason",
        "inspection_count": "Inspection Count"
    }
)

fig.write_html("quality_rejection_analysis.html")

print("Quality rejection chart created successfully!")

# Production Trend Analysis

production_df["production_date"] = pd.to_datetime(
    production_df["production_date"]
)

daily_production = production_df.groupby(
    "production_date"
).agg(
    total_target=("target_qty", "sum"),
    total_actual=("actual_qty", "sum")
).reset_index()

print("\nDaily Production Trend:")
print(daily_production.head())

# Production Trend Chart

fig = px.line(
    daily_production,
    x="production_date",
    y=["total_target", "total_actual"],
    title="Daily Production Trend",
    labels={
        "production_date": "Production Date",
        "value": "Quantity",
        "variable": "Production Type"
    },
    markers=True
)

fig.write_html("production_trend.html")

print("Production trend chart created successfully!")


# Overall KPI Summary


kpi_summary = pd.DataFrame({
    "KPI": [
        "Total Target Production",
        "Total Actual Production",
        "Total Good Production",
        "Total Rejected Production",
        "Overall Efficiency (%)",
        "Overall Rejection (%)",
        "Overall Good Quality (%)",
        "Total Breakdowns",
        "Total Downtime (Hours)"
    ],
    "Value": [
        total_target,
        total_actual,
        total_good,
        total_rejection,
        round(overall_efficiency, 2),
        round(overall_rejection, 2),
        round(overall_good_quality, 2),
        total_breakdowns,
        round(total_downtime, 2)
    ]
})

print("\nOverall KPI Summary:")
print(kpi_summary)

# Machine KPI Summary

machine_kpi_summary = machine_summary.merge(
    machine_downtime[
        ["machine_id", "total_breakdowns", "total_downtime_hours"]
    ],
    on="machine_id",
    how="left"
)

machine_kpi_summary = machine_kpi_summary[
    [
        "machine_id",
        "machine_name",
        "total_target",
        "total_actual",
        "total_good",
        "total_rejection",
        "efficiency_percentage",
        "rejection_percentage",
        "total_breakdowns",
        "total_downtime_hours"
    ]
]

print("\nMachine KPI Summary:")
print(machine_kpi_summary)





# Handle Missing Breakdown Values


machine_kpi_summary["total_breakdowns"] = (
    machine_kpi_summary["total_breakdowns"].fillna(0)
)

machine_kpi_summary["total_downtime_hours"] = (
    machine_kpi_summary["total_downtime_hours"].fillna(0)
)

machine_kpi_summary["total_breakdowns"] = (
    machine_kpi_summary["total_breakdowns"].astype(int)
)

# Machine Efficiency vs Downtime

fig = px.scatter(
    machine_kpi_summary,
    x="efficiency_percentage",
    y="total_downtime_hours",
    size="total_breakdowns",
    hover_name="machine_name",
    title="Machine Efficiency vs Downtime",
    labels={
        "efficiency_percentage": "Efficiency (%)",
        "total_downtime_hours": "Downtime (Hours)",
        "total_breakdowns": "Breakdown Count"
    }
)

fig.write_html("machine_efficiency_vs_downtime.html")

print("Machine efficiency vs downtime chart created successfully!")


# Maintenance Cost by Machine

fig = px.bar(
    machine_maintenance_summary,
    x="machine_name",
    y="total_maintenance_cost",
    title="Machine-wise Maintenance Cost",
    labels={
        "machine_name": "Machine",
        "total_maintenance_cost": "Maintenance Cost"
    }
)

fig.write_html("machine_wise_maintenance_cost.html")

print("Machine-wise maintenance cost chart created successfully!")

# Maintenance Type-wise Cost Analysis

fig = px.bar(
    maintenance_type_summary,
    x="maintenance_type",
    y="total_maintenance_cost",
    title="Maintenance Type-wise Cost",
    labels={
        "maintenance_type": "Maintenance Type",
        "total_maintenance_cost": "Maintenance Cost"
    }
)

fig.write_html("maintenance_type_cost.html")

print("Maintenance type cost chart created successfully!")

# Maintenance Type-wise Repair Hours

fig = px.bar(
    maintenance_type_summary,
    x="maintenance_type",
    y="total_repair_hours",
    title="Maintenance Type-wise Repair Hours",
    labels={
        "maintenance_type": "Maintenance Type",
        "total_repair_hours": "Repair Hours"
    }
)

fig.write_html("maintenance_type_repair_hours.html")

print("Maintenance type repair hours chart created successfully!")


#Power Bi Master dataset


def add_production_record():
    production_date = input("Production Date (YYYY-MM-DD): ")
    shift_id = int(input("Shift ID: "))
    machine_id = int(input("Machine ID: "))
    product_id = int(input("Product ID: "))

    target_qty = float(input("Target Quantity (MT): "))
    actual_qty = float(input("Actual Quantity (MT): "))
    good_qty = float(input("Good Quantity (MT): "))
    rejected_qty = float(input("Rejected Quantity (MT): "))

    # Automatic calculations
    efficiency_percentage = (
        (actual_qty / target_qty) * 100
        if target_qty > 0 else 0
    )

    rejection_percentage = (
        (rejected_qty / actual_qty) * 100
        if actual_qty > 0 else 0
    )

    good_quality_percentage = (
        (good_qty / actual_qty) * 100
        if actual_qty > 0 else 0
    )

    production_gap = target_qty - actual_qty

    # Insert production record into MySQL
    query = """
    INSERT INTO production_records
    (production_date, shift_id, machine_id, product_id,
     target_qty, actual_qty, good_qty, rejected_qty)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        production_date,
        shift_id,
        machine_id,
        product_id,
        target_qty,
        actual_qty,
        good_qty,
        rejected_qty
    )

    cursor = connection.cursor()

    cursor.execute(query, values)
    connection.commit()

    cursor.close()

    print("\n✅ Production record added successfully!")
    print(f"Efficiency: {efficiency_percentage:.2f}%")
    print(f"Rejection: {rejection_percentage:.2f}%")
    print(f"Good Quality: {good_quality_percentage:.2f}%")
    print(f"Production Gap: {production_gap:.2f} MT")


# Display valid IDs
print(shifts_df[['shift_id']])
print(machines_df[['machine_id']])
print(products_df[['product_id']])

# Add new production record

add_production_record()

print(machines_df[['machine_id', 'machine_name']])


def add_breakdown_record():
    machine_id = int(input("Machine ID: "))
    breakdown_date = input("Breakdown Date (YYYY-MM-DD): ")
    start_time = input("Start Time (YYYY-MM-DD HH:MM:SS): ")
    end_time = input("End Time (YYYY-MM-DD HH:MM:SS): ")

    breakdown_reason = input("Breakdown Reason: ")
    root_cause = input("Root Cause: ")

    # Automatic downtime calculation
    from datetime import datetime

    start = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

    downtime_hours = (end - start).total_seconds() / 3600

    query = """
    INSERT INTO breakdowns
    (machine_id, breakdown_date, start_time, end_time,
     breakdown_reason, root_cause, downtime_hours)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        machine_id,
        breakdown_date,
        start_time,
        end_time,
        breakdown_reason,
        root_cause,
        downtime_hours
    )

    cursor = connection.cursor()

    cursor.execute(query, values)
    connection.commit()

    cursor.close()

    print("\n✅ Breakdown record added successfully!")
    print(f"Downtime: {downtime_hours:.2f} Hours")

add_breakdown_record()

