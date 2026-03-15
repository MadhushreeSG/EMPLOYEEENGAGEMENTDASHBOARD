import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Employee Engagement Dashboard", layout="wide")
st.title("Employee Engagement & Burnout Prediction System")

# Load model safely
if os.path.exists("employee_model.pkl"):
    with open("employee_model.pkl","rb") as f:
        model = pickle.load(f)
else:
    st.error("Model file not found!")
    st.stop()

# Load CSV safely
if os.path.exists("Palo Alto Networks.csv"):
    df = pd.read_csv("Palo Alto Networks.csv")
else:
    st.warning("CSV file not found!")
    df = None

# Sidebar inputs
st.sidebar.header("Enter Employee Details")
job_satisfaction = st.sidebar.slider("Job Satisfaction", 1, 5, 3)
environment_satisfaction = st.sidebar.slider("Environment Satisfaction", 1, 5, 3)
work_life_balance = st.sidebar.slider("Work-Life Balance", 1, 5, 3)
overtime = st.sidebar.selectbox("Overtime", ["Yes", "No"])
years_at_company = st.sidebar.number_input("Years at Company", 0, 40, 5)
overtime_val = 1 if overtime=="Yes" else 0

# Predict burnout
if st.button("Predict Burnout Risk"):
    X_input = [[job_satisfaction, environment_satisfaction, work_life_balance, overtime_val, years_at_company]]
    prediction = model.predict(X_input)[0]
    st.success(f"Predicted Burnout Risk: {prediction}")

# Show chart if CSV exists
if df is not None:
    if "Department" in df.columns and "BurnoutLevel" in df.columns:
        fig = px.bar(df, x="Department", y="BurnoutLevel", color="BurnoutLevel", title="Burnout Levels by Department")
        st.plotly_chart(fig, use_container_width=True)
