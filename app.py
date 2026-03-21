import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Employee Engagement Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("Palo Alto Networks.csv")

df = load_data()

# ---------------- LOAD MODEL ----------------
model = None
if os.path.exists("employee_model.pkl"):
    with open("employee_model.pkl", "rb") as f:
        model = pickle.load(f)

# ---------------- SIDEBAR ----------------
st.sidebar.title("Employee Parameters")

job_satisfaction = st.sidebar.slider("Job Satisfaction", 1, 4, 2)
env_satisfaction = st.sidebar.slider("Environment Satisfaction", 1, 4, 2)
work_life = st.sidebar.slider("Work Life Balance", 1, 4, 2)
job_involvement = st.sidebar.slider("Job Involvement", 1, 4, 2)
relationship = st.sidebar.slider("Relationship Satisfaction", 1, 4, 2)

overtime = st.sidebar.selectbox("Overtime", ["No", "Yes"])
years = st.sidebar.slider("Years at Company", 0, 40, 5)

overtime_val = 1 if overtime == "Yes" else 0

# ---------------- TITLE ----------------
st.title("Employee Engagement, Satisfaction, and Burnout Diagnostic Analysis")

# ---------------- ENGAGEMENT INDEX ----------------
engagement = (job_satisfaction + env_satisfaction + job_involvement + relationship) / 4

# ---------------- BURNOUT ----------------
if overtime_val == 1 and work_life <= 2:
    burnout = "High"
elif overtime_val == 1:
    burnout = "Medium"
else:
    burnout = "Low"

# ---------------- KPI ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Engagement Index", round(engagement, 2))
col2.metric("Burnout Risk", burnout)
col3.metric("Work-Life Balance", work_life)
col4.metric("Years at Company", years)

# ---------------- PREDICTION ----------------
st.subheader("🔍 Prediction Result")

if model is not None:
    try:
        input_data = np.array([[job_satisfaction, env_satisfaction, work_life,
                                job_involvement, relationship, overtime_val, years]])
        pred = model.predict(input_data)[0]

        if pred == 1:
            st.error("High Risk: Employee May Leave")
        else:
            st.success("Low Risk: Employee Likely to Stay")
    except:
        st.warning("Model mismatch - using rule-based prediction")
        if engagement < 2.5 or burnout == "High":
            st.error("High Risk: Employee May Leave")
        else:
            st.success("Low Risk: Employee Likely to Stay")
else:
    if engagement < 2.5 or burnout == "High":
        st.error("High Risk: Employee May Leave")
    else:
        st.success("Low Risk: Employee Likely to Stay")

# ---------------- INSIGHTS ----------------
st.subheader("📊 Insights")

if overtime_val == 1:
    st.warning("Employees doing overtime have higher burnout risk")

if job_satisfaction <= 2:
    st.warning("Low job satisfaction detected")

if work_life <= 2:
    st.warning("Poor work-life balance detected")

# ---------------- DATA PREP ----------------
df["Engagement"] = (
    df["JobSatisfaction"]
    + df["EnvironmentSatisfaction"]
    + df["JobInvolvement"]
    + df["RelationshipSatisfaction"]
) / 4

# ---------------- SLIDES ----------------
st.subheader("📊 Dashboard Slides")
st.info("Use Next/Previous buttons to view insights like presentation")

if "slide" not in st.session_state:
    st.session_state.slide = 1

col1, col2, col3 = st.columns([1,2,1])

with col1:
    if st.button("⬅ Previous"):
        if st.session_state.slide > 1:
            st.session_state.slide -= 1

with col3:
    if st.button("Next ➡"):
        if st.session_state.slide < 4:
            st.session_state.slide += 1

st.write(f"### Slide {st.session_state.slide} / 4")

# -------- SLIDE 1 --------
if st.session_state.slide == 1:
    st.title("Job Satisfaction Distribution")
    fig1 = plt.figure()
    df["JobSatisfaction"].value_counts().sort_index().plot(kind="bar")
    plt.xlabel("Satisfaction Level")
    plt.ylabel("Count")
    st.pyplot(fig1)

# -------- SLIDE 2 --------
elif st.session_state.slide == 2:
    st.title("Attrition Distribution")
    fig2 = plt.figure()
    df["Attrition"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    st.pyplot(fig2)

# -------- SLIDE 3 --------
elif st.session_state.slide == 3:
    st.title("Engagement vs Years at Company")
    fig3 = plt.figure()
    plt.scatter(df["YearsAtCompany"], df["Engagement"])
    plt.xlabel("Years")
    plt.ylabel("Engagement")
    st.pyplot(fig3)

# -------- SLIDE 4 --------
elif st.session_state.slide == 4:
    st.title("Overtime vs Engagement")
    fig4 = plt.figure()
    df.groupby("OverTime")["Engagement"].mean().plot(kind="bar")
    st.pyplot(fig4)

# ---------------- FILTER ----------------
st.subheader("🔎 Filter")

dept = st.selectbox("Select Department", df["Department"].unique())
filtered = df[df["Department"] == dept]

st.write("Filtered Data Preview", filtered.head())
