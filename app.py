import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime, date, time


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Production & Maintenance Analytics System",
    page_icon="🏭",
    layout="wide"
)


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password= os.getenv("MYSQL_PASSWORD"),
        database="production_maintenance_db"
    )


def load_data(query):

    connection = get_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(query)

        data = cursor.fetchall()

        cursor.close()

        return pd.DataFrame(data)

    finally:

        connection.close()


def execute_query(query, values):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            query,
            values
        )

        connection.commit()

        cursor.close()

    finally:

        connection.close()


# ============================================================
# LOAD MASTER TABLES
# ============================================================

machines_df = load_data(
    "SELECT * FROM machines"
)

products_df = load_data(
    "SELECT * FROM products"
)

shifts_df = load_data(
    "SELECT * FROM shifts"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏭 Production System")

page = st.sidebar.radio(
    "Select Module",
    [
        "Production Entry",
        "Breakdown Entry",
        "Maintenance Entry",
        "Quality Entry",
        "Dashboard"
    ]
)


# ============================================================
# PRODUCTION ENTRY
# ============================================================

if page == "Production Entry":

    st.title("🏭 Production Entry")

    st.write(
        "Enter daily production information."
    )

    col1, col2 = st.columns(2)

    with col1:

        production_date = st.date_input(
            "Production Date",
            value=date.today()
        )

        machine_options = dict(
            zip(
                machines_df["machine_name"],
                machines_df["machine_id"]
            )
        )

        selected_machine = st.selectbox(
            "Machine",
            list(machine_options.keys())
        )

        machine_id = machine_options[
            selected_machine
        ]

        product_options = dict(
            zip(
                products_df["product_name"],
                products_df["product_id"]
            )
        )

        selected_product = st.selectbox(
            "Product",
            list(product_options.keys())
        )

        product_id = product_options[
            selected_product
        ]

    with col2:

        shift_options = dict(
            zip(
                shifts_df["shift_name"],
                shifts_df["shift_id"]
            )
        )

        selected_shift = st.selectbox(
            "Shift",
            list(shift_options.keys())
        )

        shift_id = shift_options[
            selected_shift
        ]

        target_qty = st.number_input(
            "Target Quantity (MT)",
            min_value=0.0,
            step=1.0
        )

        actual_qty = st.number_input(
            "Actual Quantity (MT)",
            min_value=0.0,
            step=1.0
        )

        good_qty = st.number_input(
            "Good Quantity (MT)",
            min_value=0.0,
            step=1.0
        )

        rejected_qty = st.number_input(
            "Rejected Quantity (MT)",
            min_value=0.0,
            step=1.0
        )

    # ========================================================
    # PRODUCTION KPI
    # ========================================================

    efficiency_percentage = (
        actual_qty / target_qty * 100
        if target_qty > 0
        else 0
    )

    rejection_percentage = (
        rejected_qty / actual_qty * 100
        if actual_qty > 0
        else 0
    )

    good_quality_percentage = (
        good_qty / actual_qty * 100
        if actual_qty > 0
        else 0
    )

    production_gap = (
        target_qty - actual_qty
    )

    st.divider()

    st.subheader(
        "Production KPIs"
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Efficiency",
        f"{efficiency_percentage:.2f}%"
    )

    k2.metric(
        "Rejection",
        f"{rejection_percentage:.2f}%"
    )

    k3.metric(
        "Good Quality",
        f"{good_quality_percentage:.2f}%"
    )

    k4.metric(
        "Production Gap",
        f"{production_gap:.2f} MT"
    )

    st.divider()

    if st.button(
        "Save Production Record",
        type="primary"
    ):

        if good_qty + rejected_qty > actual_qty:

            st.error(
                "Good Quantity + Rejected Quantity cannot be greater than Actual Quantity."
            )

        else:

            query = """
                INSERT INTO production_records
                (
                    production_date,
                    machine_id,
                    product_id,
                    shift_id,
                    target_qty,
                    actual_qty,
                    good_qty,
                    rejected_qty
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                production_date,
                machine_id,
                product_id,
                shift_id,
                target_qty,
                actual_qty,
                good_qty,
                rejected_qty
            )

            try:

                execute_query(
                    query,
                    values
                )

                st.success(
                    "Production record saved successfully."
                )

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )


# ============================================================
# BREAKDOWN ENTRY
# ============================================================

elif page == "Breakdown Entry":

    st.title("🔧 Breakdown Entry")

    st.write(
        "Record machine breakdown and calculate downtime automatically."
    )

    machine_options = dict(
        zip(
            machines_df["machine_name"],
            machines_df["machine_id"]
        )
    )

    selected_machine = st.selectbox(
        "Machine",
        list(machine_options.keys())
    )

    machine_id = machine_options[
        selected_machine
    ]

    breakdown_date = st.date_input(
        "Breakdown Date",
        value=date.today()
    )

    col1, col2 = st.columns(2)

    with col1:

        start_time = st.time_input(
            "Start Time",
            value=time(9, 0)
        )

    with col2:

        end_time = st.time_input(
            "End Time",
            value=time(10, 0)
        )

    breakdown_reason = st.text_input(
        "Breakdown Reason"
    )

    root_cause = st.text_input(
        "Root Cause"
    )

    start_datetime = datetime.combine(
        breakdown_date,
        start_time
    )

    end_datetime = datetime.combine(
        breakdown_date,
        end_time
    )

    if end_datetime > start_datetime:

        downtime_hours = (
            end_datetime - start_datetime
        ).total_seconds() / 3600

    else:

        downtime_hours = 0

    st.metric(
        "Calculated Downtime",
        f"{downtime_hours:.2f} Hours"
    )

    if st.button(
        "Save Breakdown Record",
        type="primary"
    ):

        if not breakdown_reason.strip():

            st.error(
                "Please enter breakdown reason."
            )

        elif end_datetime <= start_datetime:

            st.error(
                "End time must be greater than start time."
            )

        else:

            query = """
                INSERT INTO breakdowns
                (
                    machine_id,
                    breakdown_date,
                    start_time,
                    end_time,
                    breakdown_reason,
                    root_cause,
                    downtime_hours
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                machine_id,
                breakdown_date,
                start_datetime,
                end_datetime,
                breakdown_reason,
                root_cause,
                downtime_hours
            )

            try:

                execute_query(
                    query,
                    values
                )

                st.success(
                    "Breakdown record saved successfully."
                )

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )


# ============================================================
# MAINTENANCE ENTRY
# ============================================================

elif page == "Maintenance Entry":

    st.title("🛠️ Maintenance Entry")

    st.write(
        "Record machine maintenance activity."
    )

    machine_options = dict(
        zip(
            machines_df["machine_name"],
            machines_df["machine_id"]
        )
    )

    selected_machine = st.selectbox(
        "Machine",
        list(machine_options.keys())
    )

    machine_id = machine_options[
        selected_machine
    ]

    maintenance_date = st.date_input(
        "Maintenance Date",
        value=date.today()
    )

    maintenance_type = st.selectbox(
        "Maintenance Type",
        [
            "Preventive",
            "Breakdown",
            "Corrective",
            "Predictive"
        ]
    )

    description = st.text_area(
        "Description"
    )

    technician_name = st.text_input(
        "Technician Name"
    )

    col1, col2 = st.columns(2)

    with col1:

        repair_hours = st.number_input(
            "Repair Hours",
            min_value=0.0,
            step=0.5
        )

    with col2:

        maintenance_cost = st.number_input(
            "Maintenance Cost",
            min_value=0.0,
            step=100.0
        )

    if st.button(
        "Save Maintenance Record",
        type="primary"
    ):

        query = """
            INSERT INTO maintenance_record
            (
                machine_id,
                maintenance_date,
                maintenance_type,
                description,
                technician_name,
                repair_hours,
                maintenance_cost
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            machine_id,
            maintenance_date,
            maintenance_type,
            description,
            technician_name,
            repair_hours,
            maintenance_cost
        )

        try:

            execute_query(
                query,
                values
            )

            st.success(
                "Maintenance record saved successfully."
            )

        except Exception as e:

            st.error(
                f"Database Error: {e}"
            )


# ============================================================
# QUALITY ENTRY
# ============================================================

elif page == "Quality Entry":

    st.title("🔎 Quality Entry")

    st.write(
        "Record quality inspection."
    )

    production_df = load_data(
        """
        SELECT
            production_id,
            production_date,
            actual_qty,
            good_qty,
            rejected_qty
        FROM production_records
        ORDER BY production_id DESC
        """
    )

    if production_df.empty:

        st.warning(
            "No production records available."
        )

    else:

        production_options = {}

        for _, row in production_df.iterrows():

            label = (
                f"Production ID {row['production_id']} | "
                f"Date {row['production_date']} | "
                f"Actual {row['actual_qty']} MT"
            )

            production_options[label] = (
                row["production_id"]
            )

        selected_production = st.selectbox(
            "Production Record",
            list(production_options.keys())
        )

        production_id = production_options[
            selected_production
        ]

        inspection_date = st.date_input(
            "Inspection Date",
            value=date.today()
        )

        selected_record = production_df[
            production_df["production_id"]
            == production_id
        ].iloc[0]

        actual_qty = float(
            selected_record["actual_qty"]
        )

        st.metric(
            "Production Actual",
            f"{actual_qty:.2f} MT"
        )

        good_qty = st.number_input(
            "Good Quantity (MT)",
            min_value=0.0,
            max_value=actual_qty,
            step=1.0
        )

        rejection_reason = st.text_input(
            "Rejection Reason"
        )

        if st.button(
            "Save Quality Record",
            type="primary"
        ):

            query = """
                INSERT INTO quality_records
                (
                    production_id,
                    inspection_date,
                    good_qty,
                    rejection_reason
                )
                VALUES (%s,%s,%s,%s)
            """

            values = (
                production_id,
                inspection_date,
                good_qty,
                rejection_reason
            )

            try:

                execute_query(
                    query,
                    values
                )

                st.success(
                    "Quality record saved successfully."
                )

            except Exception as e:

                st.error(
                    f"Database Error: {e}"
                )


# ============================================================
# DASHBOARD
# ============================================================

elif page == "Dashboard":

    st.title(
        "📊 Production & Maintenance Dashboard"
    )

    st.caption(
        "Production | Machine Performance | Breakdown | Maintenance | Quality"
    )


    # ========================================================
    # LOAD DATA
    # ========================================================

    production_df = load_data(
        """
        SELECT
            p.*,
            m.machine_name,
            pr.product_name,
            s.shift_name
        FROM production_records p
        LEFT JOIN machines m
            ON p.machine_id = m.machine_id
        LEFT JOIN products pr
            ON p.product_id = pr.product_id
        LEFT JOIN shifts s
            ON p.shift_id = s.shift_id
        """
    )

    breakdowns_df = load_data(
        """
        SELECT
            b.*,
            m.machine_name
        FROM breakdowns b
        LEFT JOIN machines m
            ON b.machine_id = m.machine_id
        """
    )

    maintenance_df = load_data(
        """
        SELECT
            mr.*,
            m.machine_name
        FROM maintenance_record mr
        LEFT JOIN machines m
            ON mr.machine_id = m.machine_id
        """
    )

    quality_df = load_data(
        """
        SELECT *
        FROM quality_records
        """
    )

    schedule_df = load_data(
        """
        SELECT *
        FROM machine_schedule
        """
    )


    # ========================================================
    # DATA TYPE CONVERSION
    # ========================================================

    numeric_production_columns = [
        "target_qty",
        "actual_qty",
        "good_qty",
        "rejected_qty"
    ]

    for column in numeric_production_columns:

        if column in production_df.columns:

            production_df[column] = pd.to_numeric(
                production_df[column],
                errors="coerce"
            ).fillna(0)


    if "downtime_hours" in breakdowns_df.columns:

        breakdowns_df["downtime_hours"] = pd.to_numeric(
            breakdowns_df["downtime_hours"],
            errors="coerce"
        ).fillna(0)


    for column in [
        "repair_hours",
        "maintenance_cost"
    ]:

        if column in maintenance_df.columns:

            maintenance_df[column] = pd.to_numeric(
                maintenance_df[column],
                errors="coerce"
            ).fillna(0)


    # ========================================================
    # DATE CONVERSION
    # ========================================================

    if not production_df.empty:

        production_df["production_date"] = pd.to_datetime(
            production_df["production_date"]
        )

    if not breakdowns_df.empty:

        breakdowns_df["breakdown_date"] = pd.to_datetime(
            breakdowns_df["breakdown_date"]
        )

    if not maintenance_df.empty:

        maintenance_df["maintenance_date"] = pd.to_datetime(
            maintenance_df["maintenance_date"]
        )

    if not quality_df.empty:

        quality_df["inspection_date"] = pd.to_datetime(
            quality_df["inspection_date"]
        )


    # ========================================================
    # DASHBOARD FILTERS
    # ========================================================

    st.sidebar.divider()

    st.sidebar.subheader(
        "Dashboard Filters"
    )

    if not production_df.empty:

        min_date = production_df[
            "production_date"
        ].min().date()

        max_date = production_df[
            "production_date"
        ].max().date()

        selected_dates = st.sidebar.date_input(
            "Production Date Range",
            value=(
                min_date,
                max_date
            )
        )

        machine_filter = st.sidebar.multiselect(
            "Machine",
            sorted(
                production_df[
                    "machine_name"
                ]
                .dropna()
                .unique()
                .tolist()
            )
        )

        product_filter = st.sidebar.multiselect(
            "Product",
            sorted(
                production_df[
                    "product_name"
                ]
                .dropna()
                .unique()
                .tolist()
            )
        )

        shift_filter = st.sidebar.multiselect(
            "Shift",
            sorted(
                production_df[
                    "shift_name"
                ]
                .dropna()
                .unique()
                .tolist()
            )
        )

    else:

        selected_dates = None
        machine_filter = []
        product_filter = []
        shift_filter = []


    # ========================================================
    # FILTER PRODUCTION
    # ========================================================

    filtered_production = (
        production_df.copy()
    )

    if (
        selected_dates is not None
        and isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
        and not filtered_production.empty
    ):

        start_date = pd.Timestamp(
            selected_dates[0]
        )

        end_date = (
            pd.Timestamp(
                selected_dates[1]
            )
            + pd.Timedelta(days=1)
        )

        filtered_production = (
            filtered_production[
                (
                    filtered_production[
                        "production_date"
                    ] >= start_date
                )
                &
                (
                    filtered_production[
                        "production_date"
                    ] < end_date
                )
            ]
        )


    if machine_filter:

        filtered_production = (
            filtered_production[
                filtered_production[
                    "machine_name"
                ].isin(machine_filter)
            ]
        )


    if product_filter:

        filtered_production = (
            filtered_production[
                filtered_production[
                    "product_name"
                ].isin(product_filter)
            ]
        )


    if shift_filter:

        filtered_production = (
            filtered_production[
                filtered_production[
                    "shift_name"
                ].isin(shift_filter)
            ]
        )


    # ========================================================
    # FILTER BREAKDOWNS
    # ========================================================

    filtered_breakdowns = (
        breakdowns_df.copy()
    )

    if (
        selected_dates is not None
        and isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
        and not filtered_breakdowns.empty
    ):

        start_date = pd.Timestamp(
            selected_dates[0]
        )

        end_date = (
            pd.Timestamp(
                selected_dates[1]
            )
            + pd.Timedelta(days=1)
        )

        filtered_breakdowns = (
            filtered_breakdowns[
                (
                    filtered_breakdowns[
                        "breakdown_date"
                    ] >= start_date
                )
                &
                (
                    filtered_breakdowns[
                        "breakdown_date"
                    ] < end_date
                )
            ]
        )


    if machine_filter:

        filtered_breakdowns = (
            filtered_breakdowns[
                filtered_breakdowns[
                    "machine_name"
                ].isin(machine_filter)
            ]
        )


    # ========================================================
    # FILTER MAINTENANCE
    # ========================================================

    filtered_maintenance = (
        maintenance_df.copy()
    )

    if (
        selected_dates is not None
        and isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
        and not filtered_maintenance.empty
    ):

        start_date = pd.Timestamp(
            selected_dates[0]
        )

        end_date = (
            pd.Timestamp(
                selected_dates[1]
            )
            + pd.Timedelta(days=1)
        )

        filtered_maintenance = (
            filtered_maintenance[
                (
                    filtered_maintenance[
                        "maintenance_date"
                    ] >= start_date
                )
                &
                (
                    filtered_maintenance[
                        "maintenance_date"
                    ] < end_date
                )
            ]
        )


    if machine_filter:

        filtered_maintenance = (
            filtered_maintenance[
                filtered_maintenance[
                    "machine_name"
                ].isin(machine_filter)
            ]
        )


    # ========================================================
    # FILTER QUALITY
    # ========================================================

    filtered_quality = (
        quality_df.copy()
    )

    if not filtered_quality.empty:

        production_ids = (
            filtered_production[
                "production_id"
            ]
            .tolist()
        )

        filtered_quality = (
            filtered_quality[
                filtered_quality[
                    "production_id"
                ].isin(production_ids)
            ]
        )


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    if filtered_production.empty:

        total_target = 0
        total_actual = 0
        total_good = 0
        total_rejected = 0

    else:

        total_target = (
            filtered_production[
                "target_qty"
            ].sum()
        )

        total_actual = (
            filtered_production[
                "actual_qty"
            ].sum()
        )

        total_good = (
            filtered_production[
                "good_qty"
            ].sum()
        )

        total_rejected = (
            filtered_production[
                "rejected_qty"
            ].sum()
        )


    overall_efficiency = (
        total_actual
        / total_target
        * 100
        if total_target > 0
        else 0
    )

    overall_rejection = (
        total_rejected
        / total_actual
        * 100
        if total_actual > 0
        else 0
    )

    overall_good_quality = (
        total_good
        / total_actual
        * 100
        if total_actual > 0
        else 0
    )

    production_gap = (
        total_target
        - total_actual
    )


    total_breakdowns = len(
        filtered_breakdowns
    )

    total_downtime = (
        filtered_breakdowns[
            "downtime_hours"
        ].sum()
        if not filtered_breakdowns.empty
        else 0
    )

    total_maintenance_cost = (
        filtered_maintenance[
            "maintenance_cost"
        ].sum()
        if not filtered_maintenance.empty
        else 0
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.subheader(
        "Overall KPIs"
    )

    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Actual Production",
        f"{total_actual:.2f} MT"
    )

    k2.metric(
        "Target Production",
        f"{total_target:.2f} MT"
    )

    k3.metric(
        "Overall Efficiency",
        f"{overall_efficiency:.2f}%"
    )

    k4.metric(
        "Overall Rejection",
        f"{overall_rejection:.2f}%"
    )


    k5, k6, k7, k8 = st.columns(4)

    k5.metric(
        "Good Quality",
        f"{overall_good_quality:.2f}%"
    )

    k6.metric(
        "Production Gap",
        f"{production_gap:.2f} MT"
    )

    k7.metric(
        "Total Breakdowns",
        total_breakdowns
    )

    k8.metric(
        "Total Downtime",
        f"{total_downtime:.2f} Hrs"
    )


    st.divider()


    # ========================================================
    # OVERALL EFFICIENCY
    # ========================================================

    st.subheader(
        "Overall Efficiency"
    )

    gauge_value = min(
        max(overall_efficiency, 0),
        100
    )

    gauge_fig = px.pie(
        values=[
            gauge_value,
            100 - gauge_value
        ],
        names=[
            "Efficiency",
            "Remaining"
        ],
        hole=0.70
    )

    gauge_fig.update_traces(
        textinfo="none"
    )

    gauge_fig.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=f"{overall_efficiency:.2f}%",
                x=0.5,
                y=0.5,
                font=dict(size=28),
                showarrow=False
            )
        ],
        height=300
    )

    st.plotly_chart(
        gauge_fig,
        use_container_width=True
    )


    # ========================================================
    # MACHINE PRODUCTION EFFICIENCY
    # ========================================================

    st.subheader(
        "Machine-wise Production Efficiency"
    )

    if not filtered_production.empty:

        machine_performance = (
            filtered_production
            .groupby(
                [
                    "machine_id",
                    "machine_name"
                ]
            )
            .agg(
                Target=("target_qty", "sum"),
                Actual=("actual_qty", "sum"),
                Good=("good_qty", "sum"),
                Rejected=("rejected_qty", "sum")
            )
            .reset_index()
        )

        # IMPORTANT:
        # Convert all calculation columns to numeric

        for column in [
            "Target",
            "Actual",
            "Good",
            "Rejected"
        ]:

            machine_performance[column] = pd.to_numeric(
                machine_performance[column],
                errors="coerce"
            ).fillna(0)


        machine_performance[
            "Efficiency %"
        ] = 0.0

        machine_performance[
            "Rejection %"
        ] = 0.0


        target_mask = (
            machine_performance["Target"] > 0
        )

        actual_mask = (
            machine_performance["Actual"] > 0
        )


        machine_performance.loc[
            target_mask,
            "Efficiency %"
        ] = (
            machine_performance.loc[
                target_mask,
                "Actual"
            ]
            /
            machine_performance.loc[
                target_mask,
                "Target"
            ]
            * 100
        )


        machine_performance.loc[
            actual_mask,
            "Rejection %"
        ] = (
            machine_performance.loc[
                actual_mask,
                "Rejected"
            ]
            /
            machine_performance.loc[
                actual_mask,
                "Actual"
            ]
            * 100
        )


        machine_performance[
            "Efficiency %"
        ] = machine_performance[
            "Efficiency %"
        ].round(2)


        machine_performance[
            "Rejection %"
        ] = machine_performance[
            "Rejection %"
        ].round(2)


        fig = px.bar(
            machine_performance,
            x="machine_name",
            y="Efficiency %",
            text="Efficiency %",
            title="Machine-wise Production Efficiency"
        )

        fig.update_layout(
            xaxis_title="Machine",
            yaxis_title="Efficiency (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            machine_performance,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "No production data available."
        )


    # ========================================================
    # MACHINE TARGET VS ACTUAL
    # ========================================================

    st.subheader(
        "Machine-wise Target vs Actual"
    )

    if not filtered_production.empty:

        target_actual = (
            filtered_production
            .groupby("machine_name")
            .agg(
                Target=("target_qty", "sum"),
                Actual=("actual_qty", "sum")
            )
            .reset_index()
        )

        target_actual[
            "Target"
        ] = pd.to_numeric(
            target_actual["Target"],
            errors="coerce"
        ).fillna(0)

        target_actual[
            "Actual"
        ] = pd.to_numeric(
            target_actual["Actual"],
            errors="coerce"
        ).fillna(0)


        target_actual_long = (
            target_actual.melt(
                id_vars="machine_name",
                value_vars=[
                    "Target",
                    "Actual"
                ],
                var_name="Type",
                value_name="Quantity"
            )
        )

        fig = px.bar(
            target_actual_long,
            x="machine_name",
            y="Quantity",
            color="Type",
            barmode="group",
            title="Machine-wise Target vs Actual"
        )

        fig.update_layout(
            xaxis_title="Machine",
            yaxis_title="Quantity (MT)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # PRODUCTION TREND
    # ========================================================

    st.subheader(
        "Production Trend"
    )

    if not filtered_production.empty:

        production_trend = (
            filtered_production
            .groupby("production_date")
            .agg(
                Target=("target_qty", "sum"),
                Actual=("actual_qty", "sum")
            )
            .reset_index()
        )

        production_trend[
            "Target"
        ] = pd.to_numeric(
            production_trend["Target"],
            errors="coerce"
        ).fillna(0)

        production_trend[
            "Actual"
        ] = pd.to_numeric(
            production_trend["Actual"],
            errors="coerce"
        ).fillna(0)


        trend_long = (
            production_trend.melt(
                id_vars="production_date",
                value_vars=[
                    "Target",
                    "Actual"
                ],
                var_name="Type",
                value_name="Quantity"
            )
        )

        fig = px.line(
            trend_long,
            x="production_date",
            y="Quantity",
            color="Type",
            markers=True,
            title="Production Trend"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Quantity (MT)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # MACHINE-WISE DOWNTIME
    # ========================================================

    st.subheader(
        "Machine-wise Downtime"
    )

    if not filtered_breakdowns.empty:

        downtime_summary = (
            filtered_breakdowns
            .groupby("machine_name")
            .agg(
                Breakdown_Count=(
                    "breakdown_id",
                    "count"
                ),
                Downtime_Hours=(
                    "downtime_hours",
                    "sum"
                )
            )
            .reset_index()
        )

        downtime_summary[
            "Downtime_Hours"
        ] = pd.to_numeric(
            downtime_summary[
                "Downtime_Hours"
            ],
            errors="coerce"
        ).fillna(0)


        fig = px.bar(
            downtime_summary,
            x="machine_name",
            y="Downtime_Hours",
            text="Downtime_Hours",
            title="Machine-wise Total Downtime"
        )

        fig.update_layout(
            xaxis_title="Machine",
            yaxis_title="Downtime (Hours)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            downtime_summary,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # BREAKDOWN REASON
    # ========================================================

    st.subheader(
        "Breakdown Reason Analysis"
    )

    if not filtered_breakdowns.empty:

        reason_summary = (
            filtered_breakdowns
            .groupby("breakdown_reason")
            .agg(
                Breakdown_Count=(
                    "breakdown_id",
                    "count"
                ),
                Downtime_Hours=(
                    "downtime_hours",
                    "sum"
                )
            )
            .reset_index()
        )

        fig = px.bar(
            reason_summary,
            x="breakdown_reason",
            y="Downtime_Hours",
            text="Downtime_Hours",
            title="Breakdown Reason-wise Downtime"
        )

        fig.update_layout(
            xaxis_title="Breakdown Reason",
            yaxis_title="Downtime (Hours)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # ROOT CAUSE
    # ========================================================

    st.subheader(
        "Root Cause Analysis"
    )

    if not filtered_breakdowns.empty:

        root_cause_summary = (
            filtered_breakdowns
            .dropna(
                subset=["root_cause"]
            )
            .groupby("root_cause")
            .agg(
                Breakdown_Count=(
                    "breakdown_id",
                    "count"
                ),
                Downtime_Hours=(
                    "downtime_hours",
                    "sum"
                )
            )
            .reset_index()
        )

        if not root_cause_summary.empty:

            fig = px.bar(
                root_cause_summary,
                x="root_cause",
                y="Downtime_Hours",
                text="Downtime_Hours",
                title="Root Cause-wise Downtime"
            )

            fig.update_layout(
                xaxis_title="Root Cause",
                yaxis_title="Downtime (Hours)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # ========================================================
    # MACHINE EFFICIENCY VS DOWNTIME
    # ========================================================

    st.subheader(
        "Machine Efficiency vs Downtime"
    )

    if not filtered_production.empty:

        efficiency_machine = (
            filtered_production
            .groupby(
                [
                    "machine_id",
                    "machine_name"
                ]
            )
            .agg(
                Target=("target_qty", "sum"),
                Actual=("actual_qty", "sum")
            )
            .reset_index()
        )


        # ----------------------------------------------------
        # FIX FOR PLOTLY SCATTER ERROR
        # ----------------------------------------------------

        for column in [
            "Target",
            "Actual"
        ]:

            efficiency_machine[column] = pd.to_numeric(
                efficiency_machine[column],
                errors="coerce"
            ).fillna(0)


        efficiency_machine[
            "Efficiency %"
        ] = 0.0


        target_mask = (
            efficiency_machine["Target"] > 0
        )


        efficiency_machine.loc[
            target_mask,
            "Efficiency %"
        ] = (
            efficiency_machine.loc[
                target_mask,
                "Actual"
            ]
            /
            efficiency_machine.loc[
                target_mask,
                "Target"
            ]
            * 100
        )


        if not filtered_breakdowns.empty:

            downtime_machine = (
                filtered_breakdowns
                .groupby(
                    [
                        "machine_id",
                        "machine_name"
                    ]
                )
                .agg(
                    Downtime_Hours=(
                        "downtime_hours",
                        "sum"
                    )
                )
                .reset_index()
            )

        else:

            downtime_machine = pd.DataFrame(
                columns=[
                    "machine_id",
                    "machine_name",
                    "Downtime_Hours"
                ]
            )


        efficiency_machine = (
            efficiency_machine.merge(
                downtime_machine,
                on=[
                    "machine_id",
                    "machine_name"
                ],
                how="left"
            )
        )


        efficiency_machine[
            "Downtime_Hours"
        ] = pd.to_numeric(
            efficiency_machine[
                "Downtime_Hours"
            ],
            errors="coerce"
        ).fillna(0)


        efficiency_machine[
            "Actual"
        ] = pd.to_numeric(
            efficiency_machine[
                "Actual"
            ],
            errors="coerce"
        ).fillna(0)


        efficiency_machine[
            "Efficiency %"
        ] = pd.to_numeric(
            efficiency_machine[
                "Efficiency %"
            ],
            errors="coerce"
        ).fillna(0)


        # ----------------------------------------------------
        # SCATTER CHART
        # ----------------------------------------------------

        fig = px.scatter(
            efficiency_machine,
            x="Downtime_Hours",
            y="Efficiency %",
            size="Actual",
            hover_name="machine_name",
            title="Machine Efficiency vs Downtime"
        )

        fig.update_layout(
            xaxis_title="Downtime (Hours)",
            yaxis_title="Efficiency (%)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.dataframe(
            efficiency_machine,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # MAINTENANCE ANALYSIS
    # ========================================================

    st.subheader(
        "Maintenance Analysis"
    )

    if not filtered_maintenance.empty:

        maintenance_type_summary = (
            filtered_maintenance
            .groupby("maintenance_type")
            .agg(
                Maintenance_Cost=(
                    "maintenance_cost",
                    "sum"
                ),
                Repair_Hours=(
                    "repair_hours",
                    "sum"
                ),
                Maintenance_Count=(
                    "maintenance_id",
                    "count"
                )
            )
            .reset_index()
        )


        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                maintenance_type_summary,
                x="maintenance_type",
                y="Maintenance_Cost",
                text="Maintenance_Cost",
                title="Maintenance Type-wise Cost"
            )

            fig.update_layout(
                xaxis_title="Maintenance Type",
                yaxis_title="Cost"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        with col2:

            fig = px.bar(
                maintenance_type_summary,
                x="maintenance_type",
                y="Repair_Hours",
                text="Repair_Hours",
                title="Maintenance Type-wise Repair Hours"
            )

            fig.update_layout(
                xaxis_title="Maintenance Type",
                yaxis_title="Repair Hours"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.dataframe(
            maintenance_type_summary,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # MAINTENANCE KPI
    # ========================================================

    st.subheader(
        "Maintenance KPIs"
    )

    total_repair_hours = (
        filtered_maintenance[
            "repair_hours"
        ].sum()
        if not filtered_maintenance.empty
        else 0
    )

    maintenance_count = (
        len(filtered_maintenance)
    )


    mttr = (
        total_repair_hours
        / maintenance_count
        if maintenance_count > 0
        else 0
    )


    if not filtered_breakdowns.empty:

        breakdown_count = len(
            filtered_breakdowns
        )

        if (
            selected_dates is not None
            and isinstance(selected_dates, tuple)
            and len(selected_dates) == 2
        ):

            period_days = (
                pd.Timestamp(
                    selected_dates[1]
                )
                -
                pd.Timestamp(
                    selected_dates[0]
                )
            ).days + 1

        else:

            period_days = 1


        total_available_hours = (
            period_days * 24
        )

        mtbf = (
            total_available_hours
            / breakdown_count
            if breakdown_count > 0
            else total_available_hours
        )

    else:

        mtbf = 0


    m1, m2, m3 = st.columns(3)

    m1.metric(
        "MTTR",
        f"{mttr:.2f} Hours"
    )

    m2.metric(
        "Estimated MTBF",
        f"{mtbf:.2f} Hours"
    )

    m3.metric(
        "Maintenance Cost",
        f"{total_maintenance_cost:.2f}"
    )


    st.caption(
        "MTBF is an operational estimate based on the selected period and recorded breakdowns."
    )


    # ========================================================
    # MAINTENANCE SCHEDULE
    # ========================================================

    st.subheader(
        "Maintenance Schedule Status"
    )

    if not schedule_df.empty:

        schedule_display = (
            schedule_df.copy()
        )

        if "next_maintenance_date" in schedule_display.columns:

            schedule_display[
                "next_maintenance_date"
            ] = pd.to_datetime(
                schedule_display[
                    "next_maintenance_date"
                ]
            )

            today = pd.Timestamp(
                date.today()
            )


            schedule_display[
                "Maintenance Status"
            ] = schedule_display[
                "next_maintenance_date"
            ].apply(
                lambda x:
                "Overdue"
                if x < today
                else "Upcoming"
            )


            if "machine_id" in schedule_display.columns:

                schedule_display = (
                    schedule_display.merge(
                        machines_df[
                            [
                                "machine_id",
                                "machine_name"
                            ]
                        ],
                        on="machine_id",
                        how="left"
                    )
                )


            status_counts = (
                schedule_display[
                    "Maintenance Status"
                ]
                .value_counts()
                .reset_index()
            )


            status_counts.columns = [
                "Status",
                "Count"
            ]


            fig = px.pie(
                status_counts,
                names="Status",
                values="Count",
                title="Maintenance Schedule Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


            st.dataframe(
                schedule_display,
                use_container_width=True,
                hide_index=True
            )


        else:

            st.info(
                "next_maintenance_date column is not available."
            )


    else:

        st.info(
            "No maintenance schedule records available."
        )


    # ========================================================
    # QUALITY ANALYSIS
    # ========================================================

    st.subheader(
        "Quality Analysis"
    )

    if not filtered_production.empty:

        quality_summary = (
            filtered_production
            .groupby("production_date")
            .agg(
                Actual=("actual_qty", "sum"),
                Good=("good_qty", "sum"),
                Rejected=("rejected_qty", "sum")
            )
            .reset_index()
        )


        quality_summary[
            "Actual"
        ] = pd.to_numeric(
            quality_summary["Actual"],
            errors="coerce"
        ).fillna(0)


        quality_summary[
            "Good"
        ] = pd.to_numeric(
            quality_summary["Good"],
            errors="coerce"
        ).fillna(0)


        quality_summary[
            "Rejected"
        ] = pd.to_numeric(
            quality_summary["Rejected"],
            errors="coerce"
        ).fillna(0)


        quality_summary[
            "Rejection %"
        ] = 0.0

        quality_summary[
            "Good Quality %"
        ] = 0.0


        actual_mask = (
            quality_summary["Actual"] > 0
        )


        quality_summary.loc[
            actual_mask,
            "Rejection %"
        ] = (
            quality_summary.loc[
                actual_mask,
                "Rejected"
            ]
            /
            quality_summary.loc[
                actual_mask,
                "Actual"
            ]
            * 100
        )


        quality_summary.loc[
            actual_mask,
            "Good Quality %"
        ] = (
            quality_summary.loc[
                actual_mask,
                "Good"
            ]
            /
            quality_summary.loc[
                actual_mask,
                "Actual"
            ]
            * 100
        )


        fig = px.line(
            quality_summary,
            x="production_date",
            y=[
                "Rejection %",
                "Good Quality %"
            ],
            markers=True,
            title="Quality Trend"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Percentage"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # REJECTION REASON
    # ========================================================

    if not filtered_quality.empty:

        rejection_reason_summary = (
            filtered_quality
            .dropna(
                subset=[
                    "rejection_reason"
                ]
            )
            .groupby(
                "rejection_reason"
            )
            .agg(
                Records=(
                    "production_id",
                    "count"
                ),
                Good_Qty=(
                    "good_qty",
                    "sum"
                )
            )
            .reset_index()
        )


        if not rejection_reason_summary.empty:

            fig = px.bar(
                rejection_reason_summary,
                x="rejection_reason",
                y="Records",
                text="Records",
                title="Quality Rejection Reason Analysis"
            )

            fig.update_layout(
                xaxis_title="Rejection Reason",
                yaxis_title="Records"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # ========================================================
    # OEE INDICATOR
    # ========================================================

    st.subheader("OEE Analysis")

    if not filtered_production.empty:

        # Standard OEE cannot be calculated yet because
        # verified planned production time and ideal cycle time
        # are not available in the database.

        availability = None
        performance = None
        quality = overall_good_quality
        oee = None

    else:

        availability = None
        performance = None
        quality = 0
        oee = None

    o1, o2, o3, o4 = st.columns(4)

    o1.metric(
        "Availability",
        "N/A"
    )

    o2.metric(
        "Performance",
        "N/A"
    )

    o3.metric(
        "Quality",
        f"{quality:.2f}%"
    )

    o4.metric(
        "Standard OEE",
        "N/A"
    )

    st.caption(
        "Standard OEE is not calculated because verified planned production "
        "time and Ideal Cycle Time are not currently available in the database. "
        "Quality is calculated from actual and good production quantities."
    )


    # ========================================================
    # COMPLETE MACHINE KPI SUMMARY
    # ========================================================

    st.subheader(
        "Complete Machine KPI Summary"
    )


    if not filtered_production.empty:

        machine_kpi = (
            filtered_production
            .groupby(
                [
                    "machine_id",
                    "machine_name"
                ]
            )
            .agg(
                Target=("target_qty", "sum"),
                Actual=("actual_qty", "sum"),
                Good=("good_qty", "sum"),
                Rejected=("rejected_qty", "sum")
            )
            .reset_index()
        )


        for column in [
            "Target",
            "Actual",
            "Good",
            "Rejected"
        ]:

            machine_kpi[column] = pd.to_numeric(
                machine_kpi[column],
                errors="coerce"
            ).fillna(0)


        machine_kpi[
            "Efficiency %"
        ] = 0.0

        machine_kpi[
            "Rejection %"
        ] = 0.0


        target_mask = (
            machine_kpi["Target"] > 0
        )

        actual_mask = (
            machine_kpi["Actual"] > 0
        )


        machine_kpi.loc[
            target_mask,
            "Efficiency %"
        ] = (
            machine_kpi.loc[
                target_mask,
                "Actual"
            ]
            /
            machine_kpi.loc[
                target_mask,
                "Target"
            ]
            * 100
        )


        machine_kpi.loc[
            actual_mask,
            "Rejection %"
        ] = (
            machine_kpi.loc[
                actual_mask,
                "Rejected"
            ]
            /
            machine_kpi.loc[
                actual_mask,
                "Actual"
            ]
            * 100
        )


        if not filtered_breakdowns.empty:

            downtime_kpi = (
                filtered_breakdowns
                .groupby("machine_id")
                .agg(
                    Breakdown_Count=(
                        "breakdown_id",
                        "count"
                    ),
                    Downtime_Hours=(
                        "downtime_hours",
                        "sum"
                    )
                )
                .reset_index()
            )


            machine_kpi = (
                machine_kpi.merge(
                    downtime_kpi,
                    on="machine_id",
                    how="left"
                )
            )

        else:

            machine_kpi[
                "Breakdown_Count"
            ] = 0

            machine_kpi[
                "Downtime_Hours"
            ] = 0


        machine_kpi[
            "Breakdown_Count"
        ] = machine_kpi[
            "Breakdown_Count"
        ].fillna(0)


        machine_kpi[
            "Downtime_Hours"
        ] = machine_kpi[
            "Downtime_Hours"
        ].fillna(0)


        machine_kpi[
            "Efficiency %"
        ] = machine_kpi[
            "Efficiency %"
        ].round(2)


        machine_kpi[
            "Rejection %"
        ] = machine_kpi[
            "Rejection %"
        ].round(2)


        st.dataframe(
            machine_kpi,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # RECORD TABLES
    # ========================================================

    st.divider()

    st.subheader(
        "Production Records"
    )

    if not filtered_production.empty:

        st.dataframe(
            filtered_production,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No production records found."
        )


    st.subheader(
        "Breakdown Records"
    )

    if not filtered_breakdowns.empty:

        st.dataframe(
            filtered_breakdowns,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No breakdown records found."
        )


    st.subheader(
        "Maintenance Records"
    )

    if not filtered_maintenance.empty:

        st.dataframe(
            filtered_maintenance,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No maintenance records found."
        )


    st.subheader(
        "Quality Records"
    )

    if not filtered_quality.empty:

        st.dataframe(
            filtered_quality,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No quality records found."
        )
