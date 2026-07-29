# System Capacity & Care Load Analytics for Unaccompanied Children

## 📌 Project Overview

The **System Capacity & Care Load Analytics for Unaccompanied Children** project is a data analytics and visualization solution designed to analyze the operational flow of Unaccompanied Alien Children (UAC) through the U.S. care pipeline.

The project focuses on understanding:

- Children entering CBP custody
- Children currently in CBP custody
- Children transferred from CBP custody
- Children in HHS care
- Children discharged from HHS care
- Net intake pressure
- Care-load trends
- Potential backlog accumulation
- Capacity stress and relief periods

The project combines **Exploratory Data Analysis (EDA), data-quality validation, KPI development, time-series analysis, rolling averages, and interactive visualization** through a Streamlit dashboard.

---

## 🎯 Project Objectives

### Primary Objectives

- Analyze UAC operational data over time.
- Monitor CBP custody and care-load trends.
- Analyze transfers and discharges.
- Measure inflow versus outflow pressure.
- Identify potential periods of operational stress.
- Develop healthcare capacity-related KPIs.
- Support data-driven decision-making.
- Build an interactive Streamlit analytics dashboard.

### Secondary Objectives

- Support healthcare staffing and shelter planning.
- Improve situational awareness for policymakers.
- Identify data-quality issues.
- Provide insights for humanitarian response planning.
- Develop a foundation for future forecasting.

---

## 📊 Dataset

The dataset contains operational information related to the UAC care pipeline.

### Dataset Columns

| Column | Description |
|---|---|
| `Date` | Reporting date |
| `Children apprehended and placed in CBP custody` | Number of children entering CBP custody |
| `Children in CBP custody` | Active number of children in CBP custody |
| `Children transferred out of CBP custody` | Number of children transferred from CBP custody |
| `Children in HHS Care` | Active number of children in HHS care |
| `Children discharged from HHS Care` | Number of children discharged from HHS care |

### Dataset Summary

- **Raw records:** 1,170
- **Valid dated observations:** 720
- **Analysis period:** January 12, 2023 – December 21, 2025
- **Records without valid dates:** 450
- **Duplicate valid dates:** None

> **Important:** The supplied dataset does not contain valid observations for `Children in HHS Care`. Therefore, complete system-wide care load calculations requiring HHS occupancy data cannot be reliably calculated from the current dataset.

---

## 🔍 Data Analysis Workflow

```text
Raw Dataset
     ↓
Data Ingestion
     ↓
Data Cleaning & Validation
     ↓
Date Conversion
     ↓
Missing & Invalid Data Detection
     ↓
Exploratory Data Analysis
     ↓
Feature Engineering
     ↓
KPI Calculation
     ↓
Trend & Rolling Average Analysis
     ↓
Net Intake & Backlog Analysis
     ↓
Capacity Stress Identification
     ↓
Forecasting Framework
     ↓
Streamlit Dashboard
     ↓
Insights & Recommendations
