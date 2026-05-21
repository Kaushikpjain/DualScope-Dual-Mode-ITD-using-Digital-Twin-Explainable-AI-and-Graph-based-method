import torch
import torch.nn as nn
import numpy as np
from pymongo import MongoClient
from sklearn.preprocessing import StandardScaler

# -----------------------------
# 1. Load Digital Twin Data
# -----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
col = db["user_features"]

FEATURES = [
    "logon_events",
    "after_hours_logons",
    "file_events",
    "usb_events",
    "email_events",
    "http_total_requests",
    "http_unique_domains",
    "http_unique_topics",
    "http_after_hours",
    "http_weekend",
    "http_avg_topics",
    "O", "C", "E", "A", "N"
]

users = []
X = []

for doc in col.find({}, {"_id": 0}):
    users.append(doc["user_id"])
    X.append([doc.get(f, 0) for f in FEATURES])

X = np.array(X)

# -----------------------------
# 2. Normalize Features
# -----------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

# -----------------------------
# 3. Autoencoder Model
# -----------------------------
class AutoEncoder(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(dim, 12),
            nn.ReLU(),
            nn.Linear(12, 6),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(6, 12),
            nn.ReLU(),
            nn.Linear(12, dim)
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

model = AutoEncoder(X_tensor.shape[1])
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# -----------------------------
# 4. Train Model
# -----------------------------
print("🚀 Training Autoencoder...")

EPOCHS = 50
for epoch in range(EPOCHS):
    optimizer.zero_grad()
    recon = model(X_tensor)
    loss = criterion(recon, X_tensor)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.6f}")

print("✅ Training complete.")

# -----------------------------
# 5. Compute Anomaly Scores
# -----------------------------
with torch.no_grad():
    recon = model(X_tensor)
    errors = torch.mean((recon - X_tensor) ** 2, dim=1).numpy()

# -----------------------------
# 6. Store Results in MongoDB
# -----------------------------
scores_col = db["anomaly_scores"]
scores_col.delete_many({})

docs = []
for u, e in zip(users, errors):
    docs.append({
        "user_id": u,
        "reconstruction_error": float(e)
    })

scores_col.insert_many(docs)

print("📊 Anomaly scores stored in MongoDB.")