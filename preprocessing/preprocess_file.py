import pandas as pd
import os

INPUT = "../dataset/file.csv"
OUTPUT = "../processed_data/file_clean.csv"

chunks = []

for chunk in pd.read_csv(INPUT, chunksize=100_000):
    chunk.rename(columns={"user": "user_id", "date": "timestamp"}, inplace=True)
    chunk = chunk.dropna(subset=["user_id", "timestamp"])

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], errors="coerce")
    chunk = chunk.dropna(subset=["timestamp"])

    chunk["file_ext"] = chunk["filename"].apply(
        lambda x: os.path.splitext(str(x))[1].lower() if pd.notna(x) else "unknown"
    )

    chunk["hour"] = chunk["timestamp"].dt.hour
    chunk["day_of_week"] = chunk["timestamp"].dt.dayofweek
    chunk["is_after_hours"] = chunk["hour"].apply(lambda x: 1 if x < 8 or x > 18 else 0)

    chunk["event_type"] = "FILE"

    chunks.append(chunk)

pd.concat(chunks).to_csv(OUTPUT, index=False)
print("✅ file preprocessing done")
