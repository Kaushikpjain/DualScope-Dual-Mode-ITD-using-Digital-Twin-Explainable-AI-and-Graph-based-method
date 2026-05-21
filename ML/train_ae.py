import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler
import joblib
import os

# ---------------------------
# Load data
# ---------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]

print("Loading data from MongoDB...")
weekly = list(db.weekly_user_features.find())
df = pd.DataFrame(weekly).drop(columns=["_id", "user_id", "year", "week"])

print(f"Dataset shape: {df.shape}")

# ---------------------------
# Scale Data
# ---------------------------
scaler = StandardScaler()
X = scaler.fit_transform(df.values)
X = torch.tensor(X, dtype=torch.float32)

os.makedirs("ml/models", exist_ok=True)
joblib.dump(scaler, "ml/models/scaler.pkl")
print("✅ Scaler saved to ml/models/scaler.pkl")

# ---------------------------
# AutoEncoder Model
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
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ---------------------------
# Training Loop
# ---------------------------
print("Training AutoEncoder...")
epochs = 50
batch_size = 256
dataset = torch.utils.data.TensorDataset(X, X)
dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

for epoch in range(epochs):
    epoch_loss = 0
    for batch_x, _ in dataloader:
        optimizer.zero_grad()
        recon = model(batch_x)
        loss = criterion(recon, batch_x)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    if (epoch+1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs} | Loss: {epoch_loss/len(dataloader):.4f}")

torch.save(model.state_dict(), "ml/models/temporal_ae.pt")
print("✅ Model saved to ml/models/temporal_ae.pt")
