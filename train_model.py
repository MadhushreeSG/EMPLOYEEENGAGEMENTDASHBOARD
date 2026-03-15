import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("employee_data.csv")

# Convert categorical column
df["OverTime"] = df["OverTime"].map({"Yes":1,"No":0})

# Features
X = df[[
"JobSatisfaction",
"EnvironmentSatisfaction",
"WorkLifeBalance",
"OverTime",
"YearsAtCompany"
]]

# Target
y = df["Attrition"]

# Train model
model = RandomForestClassifier()
model.fit(X,y)

# Save model
with open("employee_model.pkl","wb") as f:
    pickle.dump(model,f)

print("Model trained successfully")
print("Pickle file created successfully!")
