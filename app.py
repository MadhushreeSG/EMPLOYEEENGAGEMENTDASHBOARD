import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Employee Engagement Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("Palo Alto Networks.csv")

df = load_data()

# ---------------- DATA PREP ----------------
df["Engagement"] = (
    df["JobSatisfaction"]
    + df["EnvironmentSatisfaction"]
    + df["JobInvolvement"]
    + df["RelationshipSatisfaction"]
) / 4

def burnout_risk(row):
    if row["OverTime"] == "Yes" and row["WorkLifeBalance"] <= 2:
        return "High"
    elif row["OverTime"] == "Yes" or row["WorkLifeBalance"] <= 2:
        return "Medium"
    else:
        return "Low"

df["BurnoutRisk"] = df.apply(burnout_risk, axis=1)

travel_map = {
    "Non-Travel": 0,
    "Travel Rarely": 1,
    "Travel Frequently": 2
}

df["StressIndicator"] = (
    (df["OverTime"] == "Yes").astype(int) +
    df["BusinessTravel"].map(travel_map).fillna(0)
) / 3


# ---------------- SIDEBAR ----------------
st.sidebar.title("Filters")

dept = st.sidebar.selectbox("Department", df["Department"].unique())

roles = df[df["Department"] == dept]["JobRole"].unique()
role = st.sidebar.selectbox("Job Role", roles)

overtime = st.sidebar.selectbox("Overtime", ["All", "Yes", "No"])

tenure = st.sidebar.slider("Years at Company", 0, 40, (0, 40))
eng_threshold = st.sidebar.slider("Engagement Threshold", 1.0, 4.0, 2.5)


# ---------------- FILTER ----------------
filtered_df = df[
    (df["Department"] == dept) &
    (df["JobRole"] == role) &
    (df["YearsAtCompany"].between(tenure[0], tenure[1]))
]

if overtime != "All":
    filtered_df = filtered_df[filtered_df["OverTime"] == overtime]

# fallback
if filtered_df.empty:
    st.warning("⚠️ No exact match, showing department data")
    filtered_df = df[df["Department"] == dept]


# ---------------- TITLE ----------------
st.title("Employee Engagement, Satisfaction, and Burnout Diagnostic Analysis at Palo Alto Networks")
st.caption(f"{dept} → {role}")


# ---------------- KPIs ----------------
eng = filtered_df["Engagement"].mean()
burn = (filtered_df["BurnoutRisk"] == "High").mean() * 100
wlb = filtered_df["WorkLifeBalance"].mean()

stability = 1 - filtered_df[[
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction"
]].std(axis=1).mean()

stress = filtered_df["StressIndicator"].mean()

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Engagement", round(eng,2))
c2.metric("High Burnout %", f"{round(burn,1)}%")
c3.metric("Work-Life Balance", round(wlb,2))
c4.metric("Stability", round(stability,2))
c5.metric("Stress", round(stress,2))


# ---------------- INSIGHTS ----------------
st.subheader("📊 Insights")

if burn > 25:
    st.error("High burnout detected")

if eng < 2.5:
    st.warning("Low engagement")

if wlb < 2.5:
    st.warning("Poor work-life balance")


# ---------------- CHARTS ----------------
st.subheader("🔥 Burnout Distribution")
st.bar_chart(filtered_df["BurnoutRisk"].value_counts())

st.subheader("📈 Engagement vs Years")
st.line_chart(filtered_df.groupby("YearsAtCompany")["Engagement"].mean())

st.subheader("📊 Overtime Impact")
st.bar_chart(filtered_df.groupby("OverTime")["Engagement"].mean())

st.subheader("📊 Job Level Engagement")
st.bar_chart(filtered_df.groupby("JobLevel")["Engagement"].mean())


# ---------------- MANAGER PANEL ----------------
st.subheader("🚨 Manager Action Panel")

low = filtered_df[filtered_df["Engagement"] < eng_threshold]
high = filtered_df[filtered_df["BurnoutRisk"] == "High"]

st.write("Low Engagement")
st.dataframe(low.head())

st.write("High Burnout")
st.dataframe(high.head())
