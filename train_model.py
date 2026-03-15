import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_csv("Palo Alto Networks.csv")

# Features and target
X = df[["JobSatisfaction","EnvironmentSatisfaction","WorkLifeBalance","Overtime","YearsAtCompany"]]
y = df["BurnoutLevel"]

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save the trained model
with open("employee_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Pickle file created successfully!")
