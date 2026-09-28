# Production & Maintenance Analytics Project

A manufacturing analytics system built to manage production, breakdown, maintenance, and quality data, analyze operational performance, and visualize business insights using Python, Streamlit, MySQL, and Power BI.

## Project Overview

This project connects a data-entry application with a MySQL database, Python-based analysis, and a Power BI dashboard.

### Project Flow

```text
User Panel (Streamlit)
        ↓
MySQL Database
        ↓
Python + Pandas Analysis
        ↓
Power BI Refresh
        ↓
Interactive Dashboard
```

## Objectives

- Record daily production information.
- Track machine breakdowns and downtime.
- Record maintenance activities, repair hours, and maintenance costs.
- Record production quality information.
- Calculate production and quality KPIs.
- Analyze machine-wise production efficiency.
- Analyze downtime and breakdown reasons.
- Analyze maintenance cost and repair hours.
- Visualize operational performance through Power BI.

## Key Features

### Production Entry

Users can enter:

- Production date
- Machine
- Product
- Shift
- Target quantity
- Actual quantity
- Good quantity
- Rejected quantity

The application calculates:

- Production efficiency
- Rejection percentage
- Good quality percentage
- Production gap

### Breakdown Entry

Users can record:

- Machine
- Breakdown date
- Start time
- End time
- Breakdown reason
- Root cause

Downtime is calculated automatically from the recorded start and end time.

### Maintenance Entry

Users can record:

- Machine
- Maintenance date
- Maintenance type
- Description
- Technician
- Repair hours
- Maintenance cost

Supported maintenance types include:

- Preventive
- Breakdown
- Corrective
- Predictive

### Quality Entry

Quality information is linked to production records and includes:

- Production record
- Inspection date
- Good quantity
- Rejection reason

## Dashboard & Analytics

The project includes a Python/Streamlit dashboard and a Power BI dashboard.

### Production KPIs

- Actual Production
- Target Production
- Overall Efficiency
- Overall Rejection
- Good Quality
- Production Gap

### Breakdown KPIs

- Total Breakdowns
- Total Downtime

### Production Analysis

- Machine-wise Production Efficiency
- Machine-wise Target vs Actual
- Production Trend

### Breakdown Analysis

- Machine-wise Downtime
- Breakdown Reason Analysis
- Root Cause Analysis
- Machine Efficiency vs Downtime

### Maintenance Analysis

- Maintenance Cost by Type
- Repair Hours by Maintenance Type
- MTTR
- Estimated MTBF
- Maintenance Cost
- Maintenance Schedule Status

### Quality Analysis

- Quality performance
- Rejection analysis
- Rejection reasons

## OEE

The project includes an OEE section.

The standard OEE calculation requires verified:

- Planned Production Time
- Downtime
- Ideal Cycle Time
- Total Count
- Good Count

The current database does not contain verified Ideal Cycle Time and Planned Production Time data required for a complete standard OEE calculation. Therefore, the application does not invent these values and shows the standard OEE as unavailable where the required data is missing.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic and analysis |
| Pandas | Data processing and analysis |
| Streamlit | Data-entry application and Python dashboard |
| MySQL | Database storage |
| SQL | Database operations and queries |
| Plotly | Interactive Python visualizations |
| Power BI Desktop | Business intelligence dashboard |
| Power Query | MySQL data connection and transformation |
| DAX | Power BI measures |
| MySQL Connector/NET | Power BI connection to MySQL |
| GitHub | Version control and project documentation |

## Database

Database name:

```text
production_maintenance_db
```

Main tables:

```text
departments
machines
products
shifts
production_records
breakdowns
maintenance_record
machine_schedule
quality_records
```

## Power BI

The Power BI dashboard is connected directly to the MySQL database.

The project supports refreshing Power BI after new records are entered into MySQL.

Example workflow:

```text
New Production / Breakdown / Maintenance / Quality Entry
                    ↓
              MySQL Database
                    ↓
             Power BI Refresh
                    ↓
          Updated Dashboard
```

## Data Validation

The Streamlit application includes validation for important inputs.

For example:

- Good quantity + rejected quantity cannot exceed actual production.
- Breakdown end time must be later than start time.
- Required breakdown and production fields must be entered before submission.
- Production KPIs are calculated from the entered quantities.

## Project Structure

A recommended repository structure is:

```text
Production-Maintenance-Analytics/
│
├── app.py
├── database_py.py
├── requirements.txt
├── README.md
│
├── sql/
│   └── database_schema.sql
│
├── powerbi/
│   └── Production_Maintenance_Dashboard.pbix
│
└── screenshots/
    ├── streamlit_production_entry.png
    ├── streamlit_breakdown_entry.png
    ├── streamlit_maintenance_entry.png
    ├── streamlit_quality_entry.png
    └── powerbi_dashboard.png
```

## Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd Production-Maintenance-Analytics
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL

Create the database:

```sql
CREATE DATABASE production_maintenance_db;
```

Import/create the required tables using the SQL schema provided in the repository.

### 4. Configure database connection

Do not commit database passwords to GitHub.

Use environment variables or a local configuration file that is excluded from Git.

Example:

```text
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=production_maintenance_db
```

### 5. Run the Streamlit application

```bash
python -m streamlit run app.py
```

## Power BI Setup

1. Install MySQL Connector/NET.
2. Open the Power BI `.pbix` file.
3. Connect Power BI to the `production_maintenance_db` MySQL database.
4. Verify the table relationships.
5. Use **Refresh** after new data is entered.

## Key Power BI Measures

### Overall Efficiency

```DAX
Overall Efficiency =
DIVIDE(
    SUM('production_maintenance_db production_records'[actual_qty]),
    SUM('production_maintenance_db production_records'[target_qty]),
    0
) * 100
```

### Overall Rejection

```DAX
Overall Rejection =
DIVIDE(
    SUM('production_maintenance_db production_records'[rejected_qty]),
    SUM('production_maintenance_db production_records'[actual_qty]),
    0
) * 100
```

### Total Breakdowns

```DAX
Total Breakdowns =
COUNT('production_maintenance_db breakdowns'[breakdown_id])
```

### Total Downtime

```DAX
Total Downtime =
SUM('production_maintenance_db breakdowns'[downtime_hours])
```

### Machine Efficiency

```DAX
Machine Efficiency =
DIVIDE(
    SUM('production_maintenance_db production_records'[actual_qty]),
    SUM('production_maintenance_db production_records'[target_qty]),
    0
) * 100
```

## Project Status

### Core Project: Completed

- MySQL database ✅
- Production Entry ✅
- Breakdown Entry ✅
- Maintenance Entry ✅
- Quality Entry ✅
- Python analysis ✅
- Streamlit application ✅
- Power BI connection ✅
- Power BI dashboard ✅
- Power BI refresh ✅
- Dashboard formatting ✅
- Data validation ✅

## Future Scope

Machine-learning features are intentionally kept outside this core project.

A separate ML mini-project can later explore areas such as:

- Machine breakdown prediction
- Downtime prediction
- Production output prediction
- Predictive maintenance

These will be developed separately rather than changing the completed analytics project.

## Author

**Sanika Karmalkar**

Mechatronics Engineering Graduate

Skills demonstrated in this project:

- Python
- SQL
- MySQL
- Pandas
- Streamlit
- Power BI
- DAX
- Power Query
- Manufacturing Analytics

---

> This project demonstrates an end-to-end manufacturing data analytics workflow from operational data entry and database storage to Python analysis and business intelligence reporting.
