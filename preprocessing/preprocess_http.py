import pandas as pd
from collections import defaultdict
from urllib.parse import urlparse

# -------------------------------
# CONFIG
# -------------------------------
INPUT = "../dataset/http.csv"
OUTPUT = "../processed_data/http_features.csv"
CHUNK_SIZE = 200_000   # safe for 13.2 GB

# -------------------------------
# Aggregation structure
# -------------------------------
user_stats = defaultdict(lambda: {
    "total_requests": 0,
    "unique_domains": set(),
    "unique_topics": set(),
    "after_hours_requests": 0,
    "weekend_requests": 0,
    "total_topics": 0
})

print("🚀 Starting HTTP preprocessing (streaming mode)...")

# -------------------------------
# Stream processing
# -------------------------------
for chunk in pd.read_csv(INPUT, chunksize=CHUNK_SIZE):
    # Normalize column names
    chunk.rename(columns={
        "user": "user_id",
        "date": "timestamp"
    }, inplace=True)

    # Drop invalid rows early
    chunk = chunk.dropna(subset=["user_id", "timestamp", "url", "content"])

    # Convert timestamp safely
    chunk["timestamp"] = pd.to_datetime(chunk["timestamp"], errors="coerce")
    chunk = chunk.dropna(subset=["timestamp"])

    # Temporal fields
    chunk["hour"] = chunk["timestamp"].dt.hour
    chunk["day_of_week"] = chunk["timestamp"].dt.dayofweek

    # Iterate row-wise (memory safe)
    for row in chunk.itertuples(index=False):
        user = row.user_id

        # Domain extraction (safe)
        try:
            domain = urlparse(row.url).netloc
        except Exception:
            domain = "unknown"

        # Topics from content
        topics = str(row.content).split()

        user_stats[user]["total_requests"] += 1
        user_stats[user]["unique_domains"].add(domain)
        user_stats[user]["unique_topics"].update(topics)
        user_stats[user]["total_topics"] += len(topics)

        # After-hours logic (README-aligned)
        if row.hour < 8 or row.hour > 18:
            user_stats[user]["after_hours_requests"] += 1

        # Weekend logic
        if row.day_of_week >= 5:
            user_stats[user]["weekend_requests"] += 1

print("✅ Finished scanning all HTTP rows.")
print("📝 Writing aggregated HTTP features...")

# -------------------------------
# Write aggregated output
# -------------------------------
rows = []
for user, s in user_stats.items():
    rows.append({
        "user_id": user,
        "total_requests": s["total_requests"],
        "unique_domains": len(s["unique_domains"]),
        "unique_topics": len(s["unique_topics"]),
        "after_hours_requests": s["after_hours_requests"],
        "weekend_requests": s["weekend_requests"],
        "avg_topics_per_page": (
            s["total_topics"] / s["total_requests"]
            if s["total_requests"] > 0 else 0
        )
    })

pd.DataFrame(rows).to_csv(OUTPUT, index=False)

print("🎉 HTTP preprocessing complete.")
print(f"📄 Output saved to: {OUTPUT}")
