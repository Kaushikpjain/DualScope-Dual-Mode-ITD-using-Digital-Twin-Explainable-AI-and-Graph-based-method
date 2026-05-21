import pandas as pd

INPUT = "../dataset/logon.csv"
OUTPUT = "../processed_data/logon_clean.csv"

chunks = []

for chunk in pd.read_csv(INPUT, chunksize=100_000):
    chunk = chunk[chunk["activity"] == "Logon"]

    chunk.rename(columns={"user": "user_id", "date": "timestamp"}, inplace=True)
    chunk = chunk.dropna(subset=["user_id", "timestamp"])

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], errors="coerce")
    chunk = chunk.dropna(subset=["timestamp"])

    chunk["hour"] = chunk["timestamp"].dt.hour
    chunk["day_of_week"] = chunk["timestamp"].dt.dayofweek
    chunk["is_after_hours"] = ((chunk["hour"] < 8) | (chunk["hour"] > 18)).astype(int)

    chunk["event_type"] = "LOGON"

    chunks.append(chunk)

pd.concat(chunks).to_csv(OUTPUT, index=False)
print("✅ logon preprocessing done")
