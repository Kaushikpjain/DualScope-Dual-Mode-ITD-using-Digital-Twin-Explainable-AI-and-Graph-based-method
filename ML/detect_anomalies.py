import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
import joblib

# ---------------------------
# Load model & scaler
# ---------------------------
scaler = joblib.load("ml/models/scaler.pkl")

class AutoEncoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim)
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

# ---------------------------
# Load data
# ---------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
weekly = list(db.weekly_user_features.find())
meta = [(d["user_id"], d["year"], d["week"]) for d in weekly]

df = pd.DataFrame(weekly).drop(columns=["_id", "user_id", "year", "week"])
X = scaler.transform(df.values)
X = torch.tensor(X, dtype=torch.float32)

model = AutoEncoder(X.shape[1])
model.load_state_dict(torch.load("ml/models/temporal_ae.pt"))
model.eval()

# ---------------------------
# Reconstruction error
# ---------------------------
with torch.no_grad():
    recon = model(X)
    errors = ((X - recon) ** 2).mean(dim=1).numpy()

threshold = np.percentile(errors, 99)  # Top 1% anomalous weeks
print("Threshold:", threshold)

# ---------------------------
# Store anomalous weeks
# ---------------------------
anomalies = db["weekly_anomalies"]
anomalies.delete_many({})

for i, err in enumerate(errors):
    if err > threshold:
        user, year, week = meta[i]
        anomalies.insert_one({
            "user_id": user,
            "year": year,
            "week": week,
            "reconstruction_error": float(err)
        })

print("✅ Weekly anomalies stored.")