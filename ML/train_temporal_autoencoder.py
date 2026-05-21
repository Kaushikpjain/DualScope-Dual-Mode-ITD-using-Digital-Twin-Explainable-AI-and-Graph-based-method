import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
import joblib

# ---------------------------
# Load data from MongoDB
# ---------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
collection = db["weekly_user_features"]

data = list(collection.find({}, {"_id": 0, "user_id": 0, "year": 0, "week": 0}))
df = pd.DataFrame(data)

print("Loaded weekly data:", df.shape)

# ---------------------------
# Scaling
# ---------------------------
scaler = StandardScaler()
X = scaler.fit_transform(df.values)

joblib.dump(scaler, "ML/models/scaler.pkl")

X = torch.tensor(X, dtype=torch.float32)

# ---------------------------
# Autoencoder Model
# ---------------------------
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

model = AutoEncoder(X.shape[1])
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
loss_fn = nn.MSELoss()

# ---------------------------
# Training
# ---------------------------
EPOCHS = 30
for epoch in range(EPOCHS):
    optimizer.zero_grad()
    output = model(X)
    loss = loss_fn(output, X)
    loss.backward()
    optimizer.step()

    if epoch % 5 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

# ---------------------------
# Save model
# ---------------------------
torch.save(model.state_dict(), "ML/models/temporal_ae.pt")
print("✅ Temporal Autoencoder trained and saved.")