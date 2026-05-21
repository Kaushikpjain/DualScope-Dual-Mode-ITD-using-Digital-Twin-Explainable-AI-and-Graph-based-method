import pandas as pd

INPUT = "../dataset/email.csv"
OUTPUT = "../processed_data/email_clean.csv"

def is_external(to_field):
    emails = str(to_field).split(";")
    return int(any(not e.strip().endswith("@dtaa.com") for e in emails))

chunks = []

for chunk in pd.read_csv(INPUT, chunksize=50_000):
    chunk.rename(columns={"user": "user_id", "date": "timestamp"}, inplace=True)
    chunk = chunk.dropna(subset=["user_id", "timestamp", "to"])

    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], errors="coerce")
    chunk = chunk.dropna(subset=["timestamp"])

    chunk["is_external"] = chunk["to"].apply(is_external)

    chunk["hour"] = chunk["timestamp"].dt.hour
    chunk["day_of_week"] = chunk["timestamp"].dt.dayofweek
    chunk["is_after_hours"] = ((chunk["hour"] < 8) | (chunk["hour"] > 18)).astype(int)

    chunk["event_type"] = "EMAIL"

    chunks.append(chunk)

pd.concat(chunks).to_csv(OUTPUT, index=False)
print("✅ email preprocessing done")
