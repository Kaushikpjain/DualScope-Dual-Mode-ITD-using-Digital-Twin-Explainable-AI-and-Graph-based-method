import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]
psy = db["psychometric"]

df = pd.read_csv("../processed_data/psychometric_clean.csv")
psy.insert_many(df.to_dict("records"))

print("✅ psychometric loaded")