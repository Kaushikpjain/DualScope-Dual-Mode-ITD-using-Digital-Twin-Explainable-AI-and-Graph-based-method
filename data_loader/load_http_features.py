import pandas as pd
from pymongo import MongoClient

# -------------------------------
# MongoDB connection
# -------------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
http_features = db["http_features"]

# -------------------------------
# Load processed HTTP features
# -------------------------------
df = pd.read_csv("../processed_data/http_features.csv")

# Optional safety: clear old data
http_features.delete_many({})

http_features.insert_many(df.to_dict("records"))

print("✅ HTTP features loaded into MongoDB")
