
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="System Capacity Dashboard",
    page_icon="🏥",
    layout="wide",
)

st.markdown(
    '<div class="main-title">🏥 System Capacity & Care Load Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Monitoring care load, intake pressure, and system capacity '
    'for Unaccompanied Children'
    '</div>',
    unsafe_allow_html=True
)

#load dataset
df = pd.read_csv("HHS_Unaccompanied_Alien_Children_Program.csv")
#Convert Date
# Remove extra spaces from column names
df.columns = df.columns.str.strip()


# ============================================================
# CONVERT DATE
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Children apprehended and placed in CBP custody*",
    "Children in CBP custody",
    "Children transferred out of CBP custody",
    "Children in HHS Care",
    "Children discharged from HHS Care"
]

for col in numeric_columns:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

#Create Metrics


df["Total System Load"] = (
    df["Children in CBP custody"].fillna(0) +
    df["Children in HHS Care"].fillna(0)
)
df["Net intake Pressure"] = (
    df["Children transferred out of CBP custody"].fillna(0) -
    df["Children discharged from HHS Care"].fillna(0)
)
df["7 Day Rolling Average"] = (df["Total System Load"].rolling(window=7).mean())
df["14 Day Rolling Average"] = (df["Total System Load"].rolling(window=14).mean())

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
print(df["Date"].dtype)
df = df.dropna(subset=["Date"])
#Sidebar Filter

start_date = st.sidebar.date_input(
    "Start Date",
    value=df["Date"].min().date()
)

end_date = st.sidebar.date_input(
    "End Date",
    value=df["Date"].max().date()
)

filtered = df[
    (df["Date"] >= pd.to_datetime(start_date)) &

    (df["Date"] <= pd.to_datetime(end_date))
]

# Month filter
months = sorted(
    df["Date"].dt.month_name().dropna().unique()
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    ["All Months"] + months
)

# Year filter
years = sorted(
    df["Date"].dt.year.dropna().unique()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All Years"] + years
)

# 5. FILTER DATA

filtered = df[
    (df["Date"] >= pd.Timestamp(start_date)) &
    (df["Date"] <= pd.Timestamp(end_date))
].copy()


# Month filter
if selected_month != "All Months":
    filtered = filtered[
        filtered["Date"].dt.month_name() == selected_month
    ]


# Year filter
if selected_year != "All Years":
    filtered = filtered[
        filtered["Date"].dt.year == selected_year
    ]

# Check if data exists
if filtered.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()

#Metric Selection

st.sidebar.subheader("📈 Metric Selector")

metric_option = st.sidebar.selectbox(
    "Select Metric",
    [
        "Total System Load",
        "Net intake Pressure",
        "Children in CBP custody",
        "Children in HHS Care",
    ]
)

metric_columns = {
    "Total System Load": "Total System Load",
    "Net intake Pressure": "Net intake Pressure",
    "Children in CBP custody": "Children in CBP custody",
    "Children in HHS Care": "Children in HHS Care"
}

selected_metric = metric_columns[metric_option]

#KPI Card

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total System Load</div>
            <div class="kpi-value">
                {filtered["Total System Load"].sum():,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Daily Load</div>
            <div class="kpi-value">
                {filtered["Total System Load"].mean():,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Peak System Load</div>
            <div class="kpi-value">
                {filtered["Total System Load"].max():,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Average Net Intake</div>
            <div class="kpi-value">
                {filtered["Net intake Pressure"].mean():,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Highest HHS Care</div>
            <div class="kpi-value">
                {filtered["Children in HHS Care"].max():,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
# CSS styling
st.markdown("""
<style>

.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: #f0f2f6 !important;
    padding: 8px !important;
    border-radius: 10px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: white !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #e3f2fd !important;
}

.stTabs [aria-selected="true"] {
    background-color: #2196f3 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)
#Tabs

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🏥 Care Load",
    "📈 Trends",
    "ℹ️ Insights"
])

#Chart of Total System Load

with tab1:
    
 st.subheader("📊 System Overview")

 st.write(
        "This section provides an overview of the total system "
        "care load."
    )
 st.line_chart(
        filtered.set_index("Date")["Total System Load"]
    )


fig, ax = plt.subplots(figsize=(12,6))
ax.plot(
    filtered["Date"],
    filtered["Total System Load"],
    color="blue"
)
ax.set_xlabel("Date")
ax.set_ylabel("Total System Load")
ax.grid(True)
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)

#CBP vs HHS

with tab2:

 st.subheader("🏥 CBP vs HHS Care Load")

 st.line_chart(
        filtered.set_index("Date")[
            [
                "Children in CBP custody",
                "Children in HHS Care"
            ]
        ]
    )
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(
    filtered["Date"],
    filtered["Children in CBP custody"],
    label = "CBP Custody",
    color = "red"
)

ax.plot(
    filtered["Date"],
    filtered["Children in HHS Care"],
    label = "HHS Care",
    color="green"
)

ax.set_xlabel("Date")
ax.set_ylabel(" Care Load")
ax.legend(["CBP Custody", "HHS Care"])
ax.grid(True)
ax.tick_params(axis="x", rotation=45)

#Net Intake


with tab3:

    st.subheader("📈 Care Load Trends")

    st.line_chart(
        filtered.set_index("Date")[
            [
                "Total System Load",
                "7 Day Rolling Average",
                "14 Day Rolling Average"
            ]
        ]
    )

    st.subheader("Net Intake Pressure")

    st.line_chart(
        filtered.set_index("Date")[
            "Net intake Pressure"
        ]
    )
fig, ax = plt.subplots(figsize=(12,6))
ax.plot(
    filtered["Date"],
    filtered["Net intake Pressure"],
    color="orange"
)
ax.axhline(
    y=0,
    linestyle="--"
)
ax.set_xlabel("Date")
ax.set_ylabel("Net Intake Pressure")
ax.grid(True)
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)

#Monthly Average Load

filtered["Month"] = filtered["Date"].dt.to_period("M")

Monthly = (filtered.groupby("Month")["Total System Load"].mean())

st.subheader("Monthly Average System Load")

st.bar_chart(Monthly)

#7 day vs 14 day rooling average

st.subheader("7 Day vs. 14 Day Rolling Average")
fig.ax = plt.subplots(figsize=(12,6))

ax.plot(
    filtered["Date"],
    filtered["Total System Load"],
    alpha=0.3,
    label="Daily System Load"
)

ax.plot(
    filtered["Date"],
    filtered["7 Day Rolling Average"],
    label="7 Day Rolling Average",
)

ax.plot(
    filtered["Date"],
    filtered["14 Day Rolling Average"],
    label="14 Day Rolling Average",
)

ax.set_xlabel("Date")
ax.set_ylabel("Children Under Care")
ax.legend()
ax.grid(True)
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)

#download filtered data
st.subheader(
    "📥 Download Filtered Data"
)

csv_data = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv_data,
    file_name="UAC_filtered_analysis.csv",
    mime="text/csv"
)

#insights and recommendation

with tab4:

 st.subheader("ℹ️ Key Insights")

 peak_load = filtered["Total System Load"].max()

 average_load = filtered["Total System Load"].mean()

 with st.expander("🔎 View Key Findings"):

    st.write(
        f"The peak total system load was "
        f"{filtered['Total System Load'].max():,.0f} children."
    )

    st.write(
        f"The average daily system load was "
        f"{filtered['Total System Load'].mean():,.0f} children."
    )

    st.write(
        "Positive net intake pressure indicates periods where "
        "transfers into HHS exceeded discharges."
    )


 with st.expander("💡 View Recommendations"):

    st.write(
        "• Monitor net intake pressure regularly."
    )

    st.write(
        "• Use rolling averages to identify sustained increases "
        "in care demand."
    )

    st.write(
        "• Use historical peak-load periods for staffing and "
        "shelter planning."
    )
st.subheader("Dataset")
st.dataframe(filtered)

# ============================================================
# CUSTOM DASHBOARD STYLING
# ============================================================

st.markdown("""
<style>

    /* Main title */
    .main-title {
        font-size: 38px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* KPI Cards */
    .kpi-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #ddd;
        background-color: #f8f9fa;
    }

    .kpi-title {
        font-size: 16px;
        font-weight: bold;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: bold;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        padding-top: 20px;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        padding: 10px;
  
/* Tab container */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    padding: 10px 0px;
}

/* Individual tabs */
.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding: 10px 20px;
    border-radius: 10px 10px 0px 0px;
    font-size: 16px;
    font-weight: 600;
}

/* Hover effect */
.stTabs [data-baseweb="tab"]:hover {
    background-color: #f0f2f6;
}

/* Active tab */
.stTabs [aria-selected="true"] {
    font-weight: bold;
}

/* Tab underline */
.stTabs [data-baseweb="tab-highlight"] {
    height: 4px;
    border-radius: 4px;
}


    /* Download button */
    .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        padding: 12px;
    }

</style>
""", unsafe_allow_html=True)














