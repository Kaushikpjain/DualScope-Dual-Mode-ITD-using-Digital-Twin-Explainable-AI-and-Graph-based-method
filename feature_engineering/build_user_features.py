import pymongo
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime
import math

# -----------------------------
# MongoDB Connection
# -----------------------------
client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]

events_col = db["events"]
http_col = db["http_features"]
psy_col = db["psychometric"]
user_features_col = db["user_features"]

# Clear old features if any
user_features_col.delete_many({})

print("🔹 Aggregating event-based features...")

# -----------------------------
# 1. EVENT-BASED FEATURES
# -----------------------------
user_stats = defaultdict(lambda: {
    "logon_events": 0,
    "after_hours_logons": 0,
    "file_events": 0,
    "usb_events": 0,
    "email_events": 0,
})

cursor = events_col.find({}, {
    "user_id": 1,
    "event_type": 1,
    "timestamp": 1
})

for ev in cursor:
    u = ev["user_id"]
    et = ev["event_type"]
    ts = ev.get("timestamp")

    # Convert timestamp string → datetime
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts)
        except Exception:
            continue

    if et == "LOGON":
        user_stats[u]["logon_events"] += 1
        if ts.hour < 8 or ts.hour > 18:
            user_stats[u]["after_hours_logons"] += 1

    elif et == "FILE":
        user_stats[u]["file_events"] += 1

    elif et == "USB":
        user_stats[u]["usb_events"] += 1

    elif et == "EMAIL":
        user_stats[u]["email_events"] += 1


print("🔹 Merging HTTP & Psychometric features...")
print("🚀 Building Digital Twin feature vectors...")

# -----------------------------
# 2. MERGE ALL FEATURES
# -----------------------------
user_ids = set(user_stats.keys())
user_ids |= set([d["user_id"] for d in http_col.find({}, {"user_id": 1})])
user_ids |= set([d["user_id"] for d in psy_col.find({}, {"user_id": 1})])

bulk_docs = []

for u in user_ids:
    doc = {"user_id": u}

    # ---- Event Features ----
    es = user_stats.get(u, {})
    doc.update({
        "logon_events": es.get("logon_events", 0),
        "after_hours_logons": es.get("after_hours_logons", 0),
        "file_events": es.get("file_events", 0),
        "usb_events": es.get("usb_events", 0),
        "email_events": es.get("email_events", 0),
    })

    # ---- HTTP Features ----
    http = http_col.find_one({"user_id": u}, {"_id": 0})
    if http:
        doc.update({
            "http_total_requests": http.get("total_requests", 0),
            "http_unique_domains": http.get("unique_domains", 0),
            "http_unique_topics": http.get("unique_topics", 0),
            "http_after_hours": http.get("after_hours_requests", 0),
            "http_weekend": http.get("weekend_requests", 0),
            "http_avg_topics": http.get("avg_topics_per_page", 0.0)
        })
    else:
        doc.update({
            "http_total_requests": 0,
            "http_unique_domains": 0,
            "http_unique_topics": 0,
            "http_after_hours": 0,
            "http_weekend": 0,
            "http_avg_topics": 0.0
        })

    # ---- Psychometric Features ----
    psy = psy_col.find_one({"user_id": u}, {"_id": 0})
    if psy:
        doc.update({
            "O": psy.get("O", 0),
            "C": psy.get("C", 0),
            "E": psy.get("E", 0),
            "A": psy.get("A", 0),
            "N": psy.get("N", 0),
        })
    else:
        doc.update({"O": 0, "C": 0, "E": 0, "A": 0, "N": 0})

    bulk_docs.append(doc)

# -----------------------------
# 3. INSERT INTO MONGODB
# -----------------------------
if bulk_docs:
    user_features_col.insert_many(bulk_docs)

print("✅ Digital Twin feature engineering completed.")
print(f"📊 Total users processed: {len(bulk_docs)}")
