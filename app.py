
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="System Capacity Dashboard",
    page_icon="🏥",
    layout="wide",
)
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
        color: black;
    }

    .kpi-value {
        font-color: Black;
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
    gap: 20px !important;
    background-color: #f0f2f6 !important;
    padding: 30px !important;
    border-radius: 20px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: white !important;
    border-radius: 30px !important;
    padding: 30px 0px !important;
    font-weight: 700 !important;
    font-size: 18px !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: #e3f2fd !important;
}

.stTabs [aria-selected="true"] {
    background-color: #2196f3 !important;
    color: white !important;
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
st.subheader("🔍 Data Quality Checks")

missing_dates = df["Date"].isna().sum()

duplicate_dates = df["Date"].duplicated().sum()

invalid_transfers = (
    df[
        df["Children transferred out of CBP custody"]
        >
        df["Children in CBP custody"]
    ]
).shape[0]

st.write(
    f"Missing dates: {missing_dates}"
)

st.write(
    f"Duplicate dates: {duplicate_dates}"
)

st.write(
    f"Potential transfer anomalies: {invalid_transfers}"
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
# Cumulative System Load
df = df.sort_values("Date").reset_index(drop=True)
df["Cumulative System Load"] = (
    df["Total System Load"].cumsum()
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

# ============================================================
# BACKLOG ANALYSIS
# ============================================================

filtered["Backlog Indicator"] = (
    filtered["Net intake Pressure"] > 0
)

backlog_days = (
    filtered["Backlog Indicator"].sum()
)


# ============================================================
# VOLATILITY ANALYSIS
# ============================================================

if filtered["Total System Load"].mean() != 0:

    volatility_index = (
        filtered["Total System Load"].std()
        / filtered["Total System Load"].mean()
    ) * 100

else:

    volatility_index = 0


# ============================================================
# CAPACITY STRESS ANALYSIS
# ============================================================

stress_threshold = filtered[
    "Total System Load"
].quantile(0.90)

stress_periods = filtered[
    filtered["Total System Load"] >= stress_threshold
]


#Discharge offset ratio


total_transfers = filtered[
    "Children transferred out of CBP custody"
].sum()

total_discharges = filtered[
    "Children discharged from HHS Care"
].sum()

if total_transfers > 0:

    discharge_offset_ratio = (
        total_discharges / total_transfers
    ) * 100

else:

    discharge_offset_ratio = 0

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
# Backlog Indicator
filtered["Backlog Indicator"] = (
    filtered["Net intake Pressure"] > 0
)

# Count number of backlog pressure days
backlog_days = filtered["Backlog Indicator"].sum()

#Discharge offset ratio
total_transfers = filtered[
    "Children transferred out of CBP custody"
].sum()

total_discharges = filtered[
    "Children discharged from HHS Care"
].sum()

if total_transfers > 0:

    discharge_offset_ratio = (
        total_discharges / total_transfers
    ) * 100

else:

    discharge_offset_ratio = 0

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
# Care Load Volatility Index
if filtered["Total System Load"].mean() != 0:
    volatility_index = (
        filtered["Total System Load"].std()
        / filtered["Total System Load"].mean()
    ) * 100
else:
    volatility_index = 0

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
#Row 1
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
st.markdown("<br>", unsafe_allow_html=True)

# Second Row
col6, col7, col8, col9, col10 = st.columns(5)  
with col6:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Care Load Volatility</div>
            <div class="kpi-value">
                {volatility_index:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col7:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Cumulative System Load</div>
            <div class="kpi-value">
                {filtered['Cumulative System Load'].iloc[-1]:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col8:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Backlog Pressure Days</div>
            <div class="kpi-value">
                {int(backlog_days)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col9:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Discharge Offset Ratio</div>
            <div class="kpi-value">
                {discharge_offset_ratio:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col10:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">High-Pressure Days</div>
            <div class="kpi-value">
                {len(stress_periods)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


#Chart of Total System Load

#Chart of Total System Load

st.subheader("Total System Load Over Time")
st.write(
    "This chart shows the total number of children under care over time, "
    "calculated by combining children in CBP custody and children in HHS care. "
    "It helps identify overall changes in system demand and periods of increasing "
    "or decreasing care load."
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

st.subheader("CBP vs. HHS Care Load Over Time")
st.write(
    "This chart compares the number of children in CBP custody "
    "with the number of children in HHS care over time. "
    "It helps identify changes in care load and differences between "
    "the two stages of the UAC care system."
)
fig, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(df["Date"], df["Children in CBP custody"], label = "CBP Custody", color="blue")
ax1.set_xlabel("Date")
ax1.set_ylabel("CBP Custody Load", color="blue")
ax1.tick_params("y", colors="blue")

 #Plot HHS custody load

ax2 = ax1.twinx()
ax2.plot(df["Date"], df["Children in HHS Care"], label = "HHS Care", color="green")
ax2.set_ylabel("HHS Care Load", color="green")
ax2.tick_params("y", colors="green")
ax1.set_title("CBP vs. HHS Care Load Over Time")
ax1.grid(True)
ax1.legend()
ax1.tick_params(axis="x", rotation=45)

st.pyplot(fig)

#Net Intake Pressrue

st.subheader("Net Intake Pressure Over Time")
st.write(
    "This chart shows the change in net intake pressure over time, "
    "calculated as the number of children transferred out of CBP "
    "custody minus the number of children discharged from HHS care. "
    "Positive values indicate that transfers exceeded discharges, "
    "which may suggest increasing pressure on the care system, "
    "while negative values indicate that discharges exceeded transfers."
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
st.write(
    "This chart shows the average system load for each month, "
    "helping to identify monthly trends, seasonal patterns, "
    "and periods of higher or lower care demand."
)
fig, ax = plt.subplots(figsize=(12,6))
ax.bar(Monthly.index.astype(str), Monthly)
ax.set_xlabel("Month")
ax.set_ylabel("Average System Load")
ax.set_title("Monthly Average System Load")
ax.tick_params(axis="x", rotation=45)

st.pyplot(fig)


#7 day vs 14 day rooling average

st.subheader("7 Day vs. 14 Day Rolling Average")
st.write(
    "This chart compares the 7-day and 14-day rolling averages "
    "of the system load to identify short-term and longer-term "
    "trends, smooth daily fluctuations, and highlight periods "
    "of increasing or decreasing care pressure."
)
fig, ax = plt.subplots(figsize=(12,6))

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



# Calculate cumulative CBP custody load
filtered["Cumulative CBP Load"] = (
    filtered["Children in CBP custody"].cumsum()
)


st.subheader("📊 Cumulative CBP Custody Load")

st.write(
    "This chart shows the cumulative reported CBP "
    "custody load across the selected reporting period."
)

fig,ax = plt.subplots(figsize=(12,6))
ax.plot(
    filtered["Date"],
    filtered["Cumulative CBP Load"]
)
ax.set_xlabel("Date")
ax.set_ylabel("Cumulative CBP Load")
ax.set_title("Cumulative CBP Custody Load")
ax.grid(True)
ax.tick_params(axis="x", rotation=45)
    

st.pyplot(fig)
#Backlog Indicator

st.subheader("📦 Backlog Pressure")
st.write(
        "This section provides an overview of Backlog Pressure "
        
    )

fig,ax = plt.subplots(figsize=(12,6))
ax.bar(
    filtered["Date"],
    filtered["Net intake Pressure"]
)
ax.set_xlabel("Date")
ax.set_ylabel("Net Intake Pressure")
ax.set_title("Backlog Pressure")
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














