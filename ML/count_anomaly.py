import numpy as np
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
scores = list(db["anomaly_scores"].find({}, {"_id": 0}))

errors = np.array([s["reconstruction_error"] for s in scores])

mean = errors.mean()
std = errors.std()
threshold = mean + 1.27 * std

anomalies = errors[errors > threshold]

print(f"Mean error: {mean:.6f}")
print(f"Std error: {std:.6f}")
print(f"Threshold: {threshold:.6f}")
print(f"Detected insiders: {len(anomalies)}")
