import streamlit as st
import pickle

model = pickle.load(open("employee_model.pkl","rb"))

st.title("Employee Engagement & Burnout Analysis")

job = st.slider("Job Satisfaction",1,4)
env = st.slider("Environment Satisfaction",1,4)
work = st.slider("Work Life Balance",1,4)
overtime = st.selectbox("Overtime",[0,1])
years = st.slider("Years At Company",0,40)

if st.button("Predict Attrition Risk"):
    prediction = model.predict([[job,env,work,overtime,years]])

    if prediction[0] == 1:
        st.error("High Risk: Employee May Leave")
    else:
        st.success("Low Attrition Risk")
