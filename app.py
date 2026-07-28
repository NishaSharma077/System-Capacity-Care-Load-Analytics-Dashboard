
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="System Capacity Dashboard",
    page_icon="🏥",
    layout="wide",
)

st.title("🏥 System Capacity & Care Load Analytics Dashboard")

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

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric(
    "Total System Load",
    int(filtered["Total System Load"].sum())
)

col2.metric(
    "Average system Load",
    int(filtered["Total System Load"].mean())
)

col3.metric(
    "Peak Load",
    int(filtered["Total System Load"].max())

)

col4.metric(
    "Average Net Intake",
    round(filtered["Net intake Pressure"].mean(), 2)
)

col5.metric(
    "Highest HHS Care",
    int(filtered["Children in HHS Care"].max())
)

#Chart of Total System Load

st.subheader("Total System Load Over Time")
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

st.subheader("Net Intake Pressure Over Time")
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

st.subheader(
    "ℹ️ Key Insights & Recommendations"
)

# Calculate insights
peak_date = filtered.loc[
    filtered["Total System Load"].idxmax(),
    "Date"
]

peak_load = filtered["Total System Load"].max()

avg_load = filtered["Total System Load"].mean()

positive_intake_days = (
    filtered["Net intake Pressure"] > 0
).sum()

total_valid_days = (
    filtered["Net intake Pressure"].notna()
    ).sum()

if total_valid_days > 0:

    positive_percentage = (
        positive_intake_days /
        total_valid_days
    ) * 100

else:

    positive_percentage = 0

# Insights
st.markdown(
    f"""
### 🔎 Key Findings

- The **peak total system load** during the selected period was
  **{peak_load:,.0f} children**, recorded on
  **{peak_date.strftime('%B %d, %Y')}**.

- The **average daily system load** was approximately
  **{avg_load:,.0f} children**.

- The system experienced **positive net intake pressure on
  {positive_percentage:.1f}% of valid reporting days**, indicating
  periods when transfers into HHS exceeded discharges.

### 💡 Recommendations

- Monitor **net intake pressure** regularly to identify potential
  increases in care demand.

- Use **7-day and 14-day rolling averages** to distinguish sustained
  changes in system load from short-term fluctuations.

- Use historical high-load periods to support **staffing and shelter
  planning**.

- Track CBP and HHS loads separately to understand where pressure
  is concentrated within the care pipeline.

- Continue monitoring the system over time to support
  **data-driven operational planning and humanitarian response**.
"""
)


st.subheader("Dataset")
st.dataframe(filtered)
