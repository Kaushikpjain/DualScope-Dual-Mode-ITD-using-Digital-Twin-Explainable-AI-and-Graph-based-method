from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["insider_threat_db"]

events_col = db["events"]
http_col = db["http_features_raw"]  # weekly HTTP aggregation input
psy_col = db["psychometric"]
weekly_col = db["weekly_user_features"]

weekly_col.delete_many({})

print("🔹 Building weekly temporal digital twins...")

# -----------------------------
# Helper: get year, week
# -----------------------------
def year_week(ts):
    return ts.isocalendar().year, ts.isocalendar().week

# -----------------------------
# 1. Aggregate EVENT features
# -----------------------------
weekly_stats = defaultdict(lambda: {
    "logon_count": 0,
    "after_hours_logons": 0,
    "file_events": 0,
    "usb_events": 0,
    "email_events": 0,
    "http_requests": 0,
    "unique_domains": set(),
    "unique_topics": set(),
    "after_hours_requests": 0,
    "weekend_requests": 0
})

print("🔹 Processing events...")

for ev in events_col.find({}, {
    "user_id": 1,
    "event_type": 1,
    "timestamp": 1
}):
    ts = ev["timestamp"]
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)

    y, w = year_week(ts)
    key = (ev["user_id"], y, w)

    if ev["event_type"] == "LOGON":
        weekly_stats[key]["logon_count"] += 1
        if ts.hour < 8 or ts.hour > 18:
            weekly_stats[key]["after_hours_logons"] += 1

    elif ev["event_type"] == "FILE":
        weekly_stats[key]["file_events"] += 1

    elif ev["event_type"] == "USB":
        weekly_stats[key]["usb_events"] += 1

    elif ev["event_type"] == "EMAIL":
        weekly_stats[key]["email_events"] += 1

# -----------------------------
# 2. Add HTTP features (Pre-aggregated)
# -----------------------------
print("🔹 Processing HTTP data (weekly)...")

# Assuming HTTP data is already per-user and can be applied across weeks,
# or we just distribute it (since timestamp is missing in the processed HTTP dataset)
for doc in http_col.find({}):
    # Since HTTP is already aggregated without a week, we will apply these baseline 
    # feature counts to the weeks the user has other activity, or create a default week 1.
    user = doc["user_id"]
    
    # Find weeks where this user already has events
    active_weeks = [(y, w) for (u, y, w) in weekly_stats.keys() if u == user]
    
    if not active_weeks:
        # If no events, just put it in a default week (2010, 1)
        active_weeks = [(2010, 1)]
        
    for y, w in active_weeks:
        key = (user, y, w)
        # Distribute / Assign the HTTP stats directly
        weekly_stats[key]["http_requests"] = doc.get("total_requests", 0)
        
        # In processed data these are just counts
        weekly_stats[key]["unique_domains"] = doc.get("unique_domains", 0)
        weekly_stats[key]["unique_topics"] = doc.get("unique_topics", 0)
        
        weekly_stats[key]["after_hours_requests"] = doc.get("after_hours_requests", 0)
        weekly_stats[key]["weekend_requests"] = doc.get("weekend_requests", 0)

# -----------------------------
# 3. Insert weekly digital twins
# -----------------------------
print("🚀 Inserting weekly digital twins...")

bulk = []
psy_map = {
    p["user_id"]: p for p in psy_col.find({}, {"_id": 0})
}

for (user, year, week), s in weekly_stats.items():
    psy = psy_map.get(user, {})

    bulk.append({
        "user_id": user,
        "year": year,
        "week": week,

        "logon_count": s["logon_count"],
        "after_hours_logons": s["after_hours_logons"],
        "file_events": s["file_events"],
        "usb_events": s["usb_events"],
        "email_events": s["email_events"],

        "http_requests": s["http_requests"],
        "unique_domains": s["unique_domains"] if isinstance(s["unique_domains"], int) else len(s["unique_domains"]),
        "unique_topics": s["unique_topics"] if isinstance(s["unique_topics"], int) else len(s["unique_topics"]),
        "after_hours_requests": s["after_hours_requests"],
        "weekend_requests": s["weekend_requests"],

        "O": psy.get("O", 0),
        "C": psy.get("C", 0),
        "E": psy.get("E", 0),
        "A": psy.get("A", 0),
        "N": psy.get("N", 0),
    })

if bulk:
    weekly_col.insert_many(bulk)

print(f"✅ Weekly digital twins created: {len(bulk)}")