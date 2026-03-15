import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load your dataset
df = pd.read_csv("Palo Alto Networks.csv")  # Make sure CSV is in same folder

# Features and target
X = df[["JobSatisfaction","EnvironmentSatisfaction","WorkLifeBalance","Overtime","YearsAtCompany"]]
y = df["BurnoutLevel"]

# Train the model
model = RandomForestClassifier()
model.fit(X, y)

# Save model as pickle
with open("employee_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Pickle file created successfully!")
