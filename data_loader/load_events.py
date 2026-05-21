import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
events = db["events"]

files = [
    "../processed_data/logon_clean.csv",
    "../processed_data/file_clean.csv",
    "../processed_data/device_clean.csv",
    "../processed_data/email_clean.csv"
]

for f in files:
    print(f"Loading {f}")
    for chunk in pd.read_csv(f, chunksize=50_000):
        events.insert_many(chunk.to_dict("records"))

print("✅ All events loaded")
