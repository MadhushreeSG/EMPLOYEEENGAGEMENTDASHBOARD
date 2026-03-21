import streamlit as st
import pickle
import numpy as np

# Load model
model = pickle.load(open("employee_model.pkl", "rb"))

# Page config
st.set_page_config(page_title="Employee Dashboard", layout="wide")

# -------------------------------
# TITLE
# -------------------------------
st.markdown(
    "<h1 style='text-align: center; color: green;'>Employee Engagement, Satisfaction, and Burnout Diagnostic Analysis at Palo Alto Networks</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Predict Employee Attrition Risk using Machine Learning</p>",
    unsafe_allow_html=True
)

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
st.sidebar.header("Employee Parameters")

job = st.sidebar.slider("Job Satisfaction", 1, 4, 2)
env = st.sidebar.slider("Environment Satisfaction", 1, 4, 2)
work = st.sidebar.slider("Work Life Balance", 1, 4, 2)
overtime = st.sidebar.selectbox("Overtime", [0, 1])
years = st.sidebar.slider("Years At Company", 0, 40, 5)

predict_btn = st.sidebar.button("Predict Risk")

# -------------------------------
# PREDICTION
# -------------------------------
if predict_btn:
    prediction = model.predict([[job, env, work, overtime, years]])
    risk = prediction[0]
else:
    risk = 0

# -------------------------------
# TOP METRICS
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Job Satisfaction", job)
col2.metric("Work-Life Balance", work)
col3.metric("Years at Company", years)
col4.metric("Overtime", overtime)

# -------------------------------
# RESULT DISPLAY
# -------------------------------
st.markdown("## 🔍 Prediction Result")

if predict_btn:
    if risk == 1:
        st.error("⚠️ High Risk: Employee May Leave")
    else:
        st.success("✅ Low Attrition Risk")

# -------------------------------
# SIMPLE ANALYSIS
# -------------------------------
st.markdown("## 📊 Insights")

if overtime == 1:
    st.warning("Employees doing overtime have higher burnout risk")

if job <= 2:
    st.warning("Low job satisfaction detected")

if work <= 2:
    st.warning("Poor work-life balance")
