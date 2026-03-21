import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Employee Engagement Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("Palo Alto Networks.csv")

df = load_data()

# ---------------- DATA PREP ----------------

# Engagement Index
df["Engagement"] = (
    df["JobSatisfaction"]
    + df["EnvironmentSatisfaction"]
    + df["JobInvolvement"]
    + df["RelationshipSatisfaction"]
) / 4

# Normalized Engagement
df["Engagement_Normalized"] = (df["Engagement"] - 1) / 3

# Burnout Risk Levels
def burnout_risk(row):
    if row["OverTime"] == "Yes" and row["WorkLifeBalance"] <= 2:
        return "High"
    elif row["OverTime"] == "Yes" or row["WorkLifeBalance"] <= 2:
        return "Medium"
    else:
        return "Low"

df["BurnoutRisk"] = df.apply(burnout_risk, axis=1)

# Travel Mapping
travel_map = {
    "Non-Travel": 0,
    "Travel_Rarely": 1,
    "Travel Frequently": 2
}

df["TravelScore"] = df["BusinessTravel"].map(travel_map)

# Stress Indicator
df["StressIndicator"] = (
    (df["OverTime"] == "Yes").astype(int) + df["TravelScore"]
) / 3


# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Filters")

dept = st.sidebar.selectbox("Department", df["Department"].unique())
role = st.sidebar.selectbox("Job Role", df["JobRole"].unique())
overtime_filter = st.sidebar.selectbox("Overtime", ["All", "Yes", "No"])
tenure = st.sidebar.slider("Years at Company", 0, 40, (0, 40))
eng_threshold = st.sidebar.slider("Engagement Threshold", 1.0, 4.0, 2.5)

filtered_df = df[
    (df["Department"] == dept) &
    (df["JobRole"] == role) &
    (df["YearsAtCompany"].between(tenure[0], tenure[1]))
]

if overtime_filter != "All":
    filtered_df = filtered_df[filtered_df["OverTime"] == overtime_filter]


# ---------------- TITLE ----------------
st.title("Employee Engagement, Satisfaction, and Burnout Analysis")

# ---------------- KPI CALCULATIONS ----------------
engagement_avg = filtered_df["Engagement"].mean()
burnout_dist = filtered_df["BurnoutRisk"].value_counts(normalize=True)
wlb_avg = filtered_df["WorkLifeBalance"].mean()

stability_score = 1 - filtered_df[[
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction"
]].std(axis=1).mean()

stress_indicator = filtered_df["StressIndicator"].mean()

# ---------------- KPI DISPLAY ----------------
col1, col2, col3, col4, col5 = st.columns(5)

eng_label = "High" if engagement_avg > 3 else "Medium" if engagement_avg > 2.5 else "Low"

col1.metric("Engagement Index", f"{round(engagement_avg,2)} ({eng_label})")
col2.metric("High Burnout %", f"{round(burnout_dist.get('High',0)*100,1)}%")
col3.metric("Work-Life Balance", round(wlb_avg, 2))
col4.metric("Stability Score", round(stability_score, 2))
col5.metric("Stress Indicator", round(stress_indicator, 2))


# ---------------- INSIGHTS ----------------
st.subheader("📊 Insights")

if burnout_dist.get("High",0) > 0.25:
    st.error("🚨 Significant high burnout segment detected")

if engagement_avg < 2.5:
    st.warning("⚠️ Engagement levels are critically low")

if wlb_avg < 2.5:
    st.warning("⚠️ Work-life balance needs improvement")

if stress_indicator > 1:
    st.warning("⚠️ Workload stress is high across employees")


# ---------------- BURNOUT DASHBOARD ----------------
st.subheader("🔥 Burnout Risk Distribution")

fig = plt.figure()
filtered_df["BurnoutRisk"].value_counts().plot(kind="bar")
st.pyplot(fig)


# ---------------- CAREER STAGE ANALYSIS ----------------
st.subheader("📊 Career Stage Analysis")

fig = plt.figure()
filtered_df.groupby("YearsAtCompany")["Engagement"].mean().plot()
plt.title("Engagement vs Years at Company")
st.pyplot(fig)

fig = plt.figure()
filtered_df.groupby("YearsInCurrentRole")["Engagement"].mean().plot()
plt.title("Engagement vs Years in Current Role")
st.pyplot(fig)


# ---------------- SLIDES ----------------
st.subheader("📈 Dashboard Slides")

if "slide" not in st.session_state:
    st.session_state.slide = 1

c1, c2, c3 = st.columns([1,2,1])

with c1:
    if st.button("⬅ Previous"):
        if st.session_state.slide > 1:
            st.session_state.slide -= 1

with c3:
    if st.button("Next ➡"):
        if st.session_state.slide < 6:
            st.session_state.slide += 1

st.write(f"### Slide {st.session_state.slide} / 6")

# -------- SLIDES --------

if st.session_state.slide == 1:
    st.title("Job Satisfaction Distribution")
    fig = plt.figure()
    filtered_df["JobSatisfaction"].value_counts().sort_index().plot(kind="bar")
    st.pyplot(fig)

elif st.session_state.slide == 2:
    st.title("Attrition Distribution")
    fig = plt.figure()
    filtered_df["Attrition"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    st.pyplot(fig)

elif st.session_state.slide == 3:
    st.title("Engagement vs Years")
    fig = plt.figure()
    plt.scatter(filtered_df["YearsAtCompany"], filtered_df["Engagement"])
    plt.xlabel("Years at Company")
    plt.ylabel("Engagement")
    st.pyplot(fig)

elif st.session_state.slide == 4:
    st.title("Overtime vs Engagement")
    fig = plt.figure()
    filtered_df.groupby("OverTime")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)

elif st.session_state.slide == 5:
    st.title("Attrition vs Engagement")
    fig = plt.figure()
    filtered_df.groupby("Attrition")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)

elif st.session_state.slide == 6:
    st.title("Engagement by Job Level")
    fig = plt.figure()
    filtered_df.groupby("JobLevel")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)


# ---------------- MANAGER ACTION PANEL ----------------
st.subheader("🚨 Manager Action Panel")

low_eng = filtered_df[filtered_df["Engagement"] < eng_threshold]
high_burn = filtered_df[filtered_df["BurnoutRisk"] == "High"]

st.write("🔻 Low Engagement Employees")
st.dataframe(low_eng.head(10))

st.write("🔥 High Burnout Risk Employees")
st.dataframe(high_burn.head(10))
