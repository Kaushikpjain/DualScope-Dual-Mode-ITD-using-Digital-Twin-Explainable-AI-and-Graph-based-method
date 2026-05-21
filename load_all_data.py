import pandas as pd
from pymongo import MongoClient

# Initialize MongoDB Connection
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]

# 1. Load Psychological Data
psy_col = db["psychometric"]
psy_col.delete_many({}) # Clear existing
psy_df = pd.read_csv("processed_data/psychometric_clean.csv")
print("Loading Psychological Data...")
psy_col.insert_many(psy_df.to_dict("records"))

# 2. Load Weekly Aggregated HTTP Features Data
http_col = db["http_features_raw"]
http_col.delete_many({})
http_df = pd.read_csv("processed_data/http_features.csv")
print("Loading HTTP Feature Data...")
for chunk in pd.read_csv("processed_data/http_features.csv", chunksize=10_000):
   http_col.insert_many(chunk.to_dict("records"))

# 3. Load Logon / File / Device Events
events_col = db["events"]
events_col.delete_many({})
files = [
    "processed_data/logon_clean.csv",
    "processed_data/file_clean.csv",
    "processed_data/device_clean.csv",
    "processed_data/email_clean.csv"
]
for f in files:
    print(f"Loading Events from {f}...")
    try:
        for chunk in pd.read_csv(f, chunksize=50_000):
            events_col.insert_many(chunk.to_dict("records"))
    except Exception as e:
        print(f"Error loading {f}: {e}")

print("✅ All preprocessed datasets successfully loaded into MongoDB!")
