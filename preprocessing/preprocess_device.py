import pandas as pd

INPUT = "../dataset/device.csv"
OUTPUT = "../processed_data/device_clean.csv"

chunks = []

for chunk in pd.read_csv(INPUT, chunksize=50_000):
    chunk.rename(columns={"user": "user_id", "date": "timestamp"}, inplace=True)
    chunk = chunk.dropna(subset=["user_id", "timestamp"])

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], errors="coerce")
    chunk = chunk.dropna(subset=["timestamp"])

    chunk["is_usb_insert"] = chunk["activity"].apply(
        lambda x: 1 if str(x).lower() == "connect" else 0
    )

    chunk["hour"] = chunk["timestamp"].dt.hour
    chunk["day_of_week"] = chunk["timestamp"].dt.dayofweek
    chunk["is_after_hours"] = chunk["hour"].apply(lambda x: 1 if x < 8 or x > 18 else 0)

    chunk["event_type"] = "USB"

    chunks.append(chunk)

pd.concat(chunks).to_csv(OUTPUT, index=False)
print("✅ device preprocessing done")
