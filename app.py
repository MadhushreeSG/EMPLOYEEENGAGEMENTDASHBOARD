import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt

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

df["BurnoutFlag"] = ((df["OverTime"] == "Yes") & (df["WorkLifeBalance"] <= 2)).astype(int)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Filters")

dept = st.sidebar.selectbox("Department", df["Department"].unique())
role = st.sidebar.selectbox("Job Role", df["JobRole"].unique())
overtime_filter = st.sidebar.selectbox("Overtime", ["All", "Yes", "No"])
tenure = st.sidebar.slider("Years at Company", 0, 40, (0, 40))

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
burnout_rate = filtered_df["BurnoutFlag"].mean()
wlb_avg = filtered_df["WorkLifeBalance"].mean()

stability_score = filtered_df[[
    "JobSatisfaction",
    "EnvironmentSatisfaction",
    "RelationshipSatisfaction"
]].std(axis=1).mean()

stress_indicator = (
    (filtered_df["OverTime"] == "Yes").mean() +
    filtered_df["BusinessTravel"].value_counts(normalize=True).get("Travel_Frequently", 0)
)

# ---------------- KPI DISPLAY ----------------
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Engagement Index", round(engagement_avg, 2))
col2.metric("Burnout Risk %", f"{round(burnout_rate*100,1)}%")
col3.metric("Work-Life Balance", round(wlb_avg, 2))
col4.metric("Stability Score", round(stability_score, 2))
col5.metric("Stress Indicator", round(stress_indicator, 2))

# ---------------- INSIGHTS ----------------
st.subheader("📊 Insights")

if burnout_rate > 0.3:
    st.error("High burnout risk detected in this segment")

if engagement_avg < 2.5:
    st.warning("Low engagement levels observed")

if wlb_avg < 2:
    st.warning("Poor work-life balance across employees")

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

# 1 Satisfaction
if st.session_state.slide == 1:
    st.title("Job Satisfaction Distribution")
    fig = plt.figure()
    filtered_df["JobSatisfaction"].value_counts().sort_index().plot(kind="bar")
    st.pyplot(fig)

# 2 Attrition
elif st.session_state.slide == 2:
    st.title("Attrition Distribution")
    fig = plt.figure()
    filtered_df["Attrition"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    st.pyplot(fig)

# 3 Engagement vs Years
elif st.session_state.slide == 3:
    st.title("Engagement vs Years")
    fig = plt.figure()
    plt.scatter(filtered_df["YearsAtCompany"], filtered_df["Engagement"])
    st.pyplot(fig)

# 4 Overtime Impact
elif st.session_state.slide == 4:
    st.title("Overtime vs Engagement")
    fig = plt.figure()
    filtered_df.groupby("OverTime")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)

# 5 Attrition vs Engagement
elif st.session_state.slide == 5:
    st.title("Attrition vs Engagement")
    fig = plt.figure()
    filtered_df.groupby("Attrition")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)

# 6 Job Level Analysis
elif st.session_state.slide == 6:
    st.title("Engagement by Job Level")
    fig = plt.figure()
    filtered_df.groupby("JobLevel")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig)

# ---------------- BURNOUT TABLE ----------------
st.subheader("🔥 High Burnout Employees")

burnout_df = filtered_df[
    (filtered_df["OverTime"] == "Yes") &
    (filtered_df["WorkLifeBalance"] <= 2)
]

st.write(burnout_df.head())

