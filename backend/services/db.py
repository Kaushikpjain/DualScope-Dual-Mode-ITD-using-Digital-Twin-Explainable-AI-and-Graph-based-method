import os
from pymongo import MongoClient

# MongoDB connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URI)
    db = client["insider_threat_db"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    db = None


# ─────────────────────────────────────────────
#  Dashboard Summary
# ─────────────────────────────────────────────
def get_dashboard_summary():
    """Aggregate real counts from the database."""
    if db is None:
        return {}

    total_users = db["psychometric"].count_documents({})
    total_events = db["events"].estimated_document_count()
    total_anomalous_weeks = db["weekly_anomalies"].count_documents({})

    # Users whose reconstruction error is in the top 1% are considered threats
    scores = list(db["anomaly_scores"].find({}, {"_id": 0}).sort("reconstruction_error", -1))
    threshold_idx = max(1, int(len(scores) * 0.01))
    threat_users = scores[:threshold_idx]
    threat_count = len(threat_users)

    # Suspicious = top 6.7% minus threats (~67 total flagged, aligned with CERT r4.2 ground truth)
    suspicious_idx = max(1, int(len(scores) * 0.067))
    suspicious_count = suspicious_idx - threat_count

    return {
        "total_users": total_users,
        "total_events": total_events,
        "total_anomalous_weeks": total_anomalous_weeks,
        "confirmed_threats": threat_count,
        "suspicious_users": suspicious_count,
        "threat_user_ids": [u["user_id"] for u in threat_users],
    }


# ─────────────────────────────────────────────
#  User Lists & Search
# ─────────────────────────────────────────────
def get_all_users_with_risk(limit=50, offset=0):
    """Return users ordered by risk (reconstruction error) descending."""
    if db is None:
        return []

    pipeline = [
        {"$sort": {"reconstruction_error": -1}},
        {"$skip": offset},
        {"$limit": limit},
        {"$lookup": {
            "from": "psychometric",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "psy"
        }},
        {"$lookup": {
            "from": "weekly_anomalies",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "anomalies"
        }},
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "reconstruction_error": 1,
            "anomalous_weeks": {"$size": "$anomalies"},
            "O": {"$arrayElemAt": ["$psy.O", 0]},
            "C": {"$arrayElemAt": ["$psy.C", 0]},
            "E": {"$arrayElemAt": ["$psy.E", 0]},
            "A": {"$arrayElemAt": ["$psy.A", 0]},
            "N": {"$arrayElemAt": ["$psy.N", 0]},
        }}
    ]
    return list(db["anomaly_scores"].aggregate(pipeline))


def search_users(query: str, limit=20):
    """Search users by user_id prefix/substring."""
    if db is None or not query:
        return []

    pipeline = [
        {"$match": {"user_id": {"$regex": query, "$options": "i"}}},
        {"$sort": {"reconstruction_error": -1}},
        {"$limit": limit},
        {"$lookup": {
            "from": "weekly_anomalies",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "anomalies"
        }},
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "reconstruction_error": 1,
            "anomalous_weeks": {"$size": "$anomalies"},
        }}
    ]
    return list(db["anomaly_scores"].aggregate(pipeline))


# ─────────────────────────────────────────────
#  User Behavior (Digital Twin)
# ─────────────────────────────────────────────
def get_weekly_features(user_id: str):
    """Return weekly feature vectors for a given user, sorted by time."""
    if db is None:
        return []
    return list(
        db["weekly_user_features"]
        .find({"user_id": user_id}, {"_id": 0})
        .sort([("year", 1), ("week", 1)])
    )


def get_anomalies(user_id: str = None):
    """Return anomalous weeks, optionally filtered by user."""
    if db is None:
        return []
    query = {}
    if user_id:
        query["user_id"] = user_id
    return list(db["weekly_anomalies"].find(query, {"_id": 0}))


def get_user_psychometric(user_id: str):
    """Return a single user's psychometric profile."""
    if db is None:
        return {}
    return db["psychometric"].find_one({"user_id": user_id}, {"_id": 0}) or {}


def get_user_explain(user_id: str):
    """
    Enhanced XAI: Compute feature-level contribution to anomaly for a user.
    Returns 1-100 scaled scores, natural language explanation, and risk breakdown.
    """
    if db is None:
        return {}

    FEATURE_COLS = [
        "logon_count", "after_hours_logons", "file_events",
        "usb_events", "email_events", "http_requests",
        "unique_domains", "unique_topics",
        "after_hours_requests", "weekend_requests"
    ]

    FEATURE_LABELS = {
        "logon_count": "Login Activity",
        "after_hours_logons": "After-Hours Logins",
        "file_events": "File Access",
        "usb_events": "USB Device Usage",
        "email_events": "Email Activity",
        "http_requests": "Web Browsing",
        "unique_domains": "Unique Websites",
        "unique_topics": "Content Topics",
        "after_hours_requests": "After-Hours Browsing",
        "weekend_requests": "Weekend Activity"
    }

    user_weeks = list(
        db["weekly_user_features"].find({"user_id": user_id}, {"_id": 0})
    )
    if not user_weeks:
        return {}

    # User averages
    user_avg = {}
    for f in FEATURE_COLS:
        vals = [w.get(f, 0) for w in user_weeks]
        user_avg[f] = sum(vals) / len(vals) if vals else 0

    # Global averages (sample 5000 docs for speed)
    global_sample = list(db["weekly_user_features"].aggregate([
        {"$sample": {"size": 5000}},
        {"$group": {
            "_id": None,
            **{f: {"$avg": f"${f}"} for f in FEATURE_COLS}
        }}
    ]))

    if not global_sample:
        return {}
    global_avg = global_sample[0]

    # Deviation-based contributions (raw)
    raw_deviations = []
    for f in FEATURE_COLS:
        g = global_avg.get(f, 0) or 1
        deviation = abs(user_avg[f] - g) / abs(g) if g else 0
        direction = "above" if user_avg[f] > g else "below"
        raw_deviations.append({
            "feature": f,
            "label": FEATURE_LABELS.get(f, f),
            "user_value": round(user_avg[f], 2),
            "global_avg": round(g, 2),
            "raw_deviation": round(deviation, 4),
            "direction": direction
        })

    # Scale deviations to 1-100
    max_dev = max(d["raw_deviation"] for d in raw_deviations) if raw_deviations else 1
    if max_dev == 0:
        max_dev = 1

    for d in raw_deviations:
        d["score"] = max(1, min(100, round(d["raw_deviation"] / max_dev * 100)))

    raw_deviations.sort(key=lambda x: x["score"], reverse=True)
    contributions = raw_deviations[:8]

    # Get anomaly score and risk level (using percentile-based thresholds)
    score_doc = db["anomaly_scores"].find_one({"user_id": user_id}, {"_id": 0})
    risk_score = score_doc.get("reconstruction_error", 0) if score_doc else 0

    anomaly_count = db["weekly_anomalies"].count_documents({"user_id": user_id})
    total_weeks = len(user_weeks)

    # Compute percentile thresholds from all users
    all_scores = [s["reconstruction_error"] for s in db["anomaly_scores"].find({}, {"reconstruction_error": 1, "_id": 0})]
    all_scores.sort()
    n = len(all_scores)
    p99 = all_scores[int(n * 0.99)] if n > 0 else 0   # Top 1% = CRITICAL
    p93 = all_scores[int(n * 0.93)] if n > 0 else 0   # Top 7% = HIGH
    p85 = all_scores[int(n * 0.85)] if n > 0 else 0   # Top 15% = MEDIUM

    if risk_score >= p99:
        risk_level = "CRITICAL"
    elif risk_score >= p93:
        risk_level = "HIGH"
    elif risk_score >= p85:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # Psychometric data
    psy = db["psychometric"].find_one({"user_id": user_id}, {"_id": 0}) or {}

    # Natural language explanation
    top3 = contributions[:3]
    reasons = []
    for c in top3:
        pct = round(c["raw_deviation"] * 100)
        if c["direction"] == "above":
            reasons.append(f'{c["label"]} is {pct}% above the organizational average '
                          f'(user: {c["user_value"]:.1f} vs avg: {c["global_avg"]:.1f})')
        else:
            reasons.append(f'{c["label"]} is {pct}% below the organizational average '
                          f'(user: {c["user_value"]:.1f} vs avg: {c["global_avg"]:.1f})')

    summary = (
        f'User {user_id} was flagged as {risk_level} risk with a reconstruction error of '
        f'{risk_score:.4f}. The system detected {anomaly_count} anomalous weeks out of '
        f'{total_weeks} total weeks monitored. '
        f'The primary reasons for flagging are: {"; ".join(reasons)}.'
    )

    return {
        "contributions": contributions,
        "summary": summary,
        "risk_score": round(risk_score, 6),
        "risk_level": risk_level,
        "anomalous_weeks": anomaly_count,
        "total_weeks": total_weeks,
        "anomaly_rate": round(anomaly_count / total_weeks * 100, 1) if total_weeks else 0,
        "psychometric": {
            "O": round(psy.get("O", 0), 2),
            "C": round(psy.get("C", 0), 2),
            "E": round(psy.get("E", 0), 2),
            "A": round(psy.get("A", 0), 2),
            "N": round(psy.get("N", 0), 2),
        } if psy else None,
    }


# ─────────────────────────────────────────────
#  Analytics & Aggregations
# ─────────────────────────────────────────────
def get_activity_distribution():
    """Count events by type (LOGON, FILE, USB, EMAIL)."""
    if db is None:
        return []
    pipeline = [
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(db["events"].aggregate(pipeline))
    return [{"event_type": r["_id"], "count": r["count"]} for r in results]


def get_top_risky_users(n=10):
    """Return top N users by reconstruction error."""
    if db is None:
        return []
    return list(
        db["anomaly_scores"]
        .find({}, {"_id": 0})
        .sort("reconstruction_error", -1)
        .limit(n)
    )


def get_weekly_anomaly_trend():
    """Return count of anomalies per (year, week) for timeline chart."""
    if db is None:
        return []
    pipeline = [
        {"$group": {
            "_id": {"year": "$year", "week": "$week"},
            "count": {"$sum": 1},
            "avg_error": {"$avg": "$reconstruction_error"}
        }},
        {"$sort": {"_id.year": 1, "_id.week": 1}},
        {"$project": {
            "_id": 0,
            "year": "$_id.year",
            "week": "$_id.week",
            "count": 1,
            "avg_error": {"$round": ["$avg_error", 6]}
        }}
    ]
    return list(db["weekly_anomalies"].aggregate(pipeline))


def get_psychometric_risk_correlation():
    """Combine anomaly scores with psychometric data for scatter analysis."""
    if db is None:
        return []
    pipeline = [
        {"$sort": {"reconstruction_error": -1}},
        {"$limit": 100},
        {"$lookup": {
            "from": "psychometric",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "psy"
        }},
        {"$unwind": {"path": "$psy", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "user_id": 1,
            "reconstruction_error": {"$round": ["$reconstruction_error", 6]},
            "O": "$psy.O",
            "C": "$psy.C",
            "E": "$psy.E",
            "A": "$psy.A",
            "N": "$psy.N",
        }}
    ]
    return list(db["anomaly_scores"].aggregate(pipeline))


# ─────────────────────────────────────────────
#  Per-User Activity Graph
# ─────────────────────────────────────────────
def get_user_activity_graph(user_id: str):
    """
    Build a per-user activity graph for forensic visualization.
    Central user node → connected activity nodes grouped by (event_type, year, week).
    Each activity node is risk-colored based on anomaly detection results.
    """
    if db is None:
        return {"nodes": [], "links": [], "user_id": user_id}

    # 1. Aggregate events by (event_type, year, week) with details
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$addFields": {
            "parsed_ts": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$timestamp"}, "string"]},
                    "then": {"$dateFromString": {"dateString": "$timestamp"}},
                    "else": "$timestamp"
                }
            }
        }},
        {"$addFields": {
            "year": {"$isoWeekYear": "$parsed_ts"},
            "week": {"$isoWeek": "$parsed_ts"},
            "hour": {"$hour": "$parsed_ts"},
            "day_of_week": {"$isoDayOfWeek": "$parsed_ts"},
        }},
        {"$group": {
            "_id": {
                "event_type": "$event_type",
                "year": "$year",
                "week": "$week",
            },
            "count": {"$sum": 1},
            "after_hours_count": {
                "$sum": {"$cond": [
                    {"$or": [{"$lt": ["$hour", 8]}, {"$gt": ["$hour", 18]}]},
                    1, 0
                ]}
            },
            "weekend_count": {
                "$sum": {"$cond": [{"$gte": ["$day_of_week", 6]}, 1, 0]}
            },
            "pcs": {"$addToSet": "$pc"},
            "sample_timestamp": {"$first": "$parsed_ts"},
        }},
        {"$sort": {"_id.year": 1, "_id.week": 1, "_id.event_type": 1}},
    ]
    activity_groups = list(db["events"].aggregate(pipeline, allowDiskUse=True))

    if not activity_groups:
        return {"nodes": [], "links": [], "user_id": user_id}

    # 2. Get anomalous weeks for this user
    anomaly_set = set()
    anomaly_errors = {}
    for a in db["weekly_anomalies"].find({"user_id": user_id}, {"_id": 0}):
        key = (a.get("year"), a.get("week"))
        anomaly_set.add(key)
        anomaly_errors[key] = a.get("reconstruction_error", 0)

    # 3. Get user's overall risk score
    score_doc = db["anomaly_scores"].find_one({"user_id": user_id}, {"_id": 0})
    user_risk = score_doc.get("reconstruction_error", 0) if score_doc else 0

    # 4. Get psychometric data
    psy = db["psychometric"].find_one({"user_id": user_id}, {"_id": 0}) or {}

    # 5. Get per-week feature data for detail display
    weekly_features = {}
    for wf in db["weekly_user_features"].find({"user_id": user_id}, {"_id": 0}):
        key = (wf.get("year"), wf.get("week"))
        weekly_features[key] = wf

    # 6. Build graph nodes and links
    nodes = []
    links = []

    # Central user node
    user_node_id = f"user_{user_id}"
    nodes.append({
        "id": user_node_id,
        "label": user_id,
        "type": "user",
        "risk_score": round(user_risk, 4),
        "psychometric": {
            "O": round(psy.get("O", 0), 2),
            "C": round(psy.get("C", 0), 2),
            "E": round(psy.get("E", 0), 2),
            "A": round(psy.get("A", 0), 2),
            "N": round(psy.get("N", 0), 2),
        } if psy else None,
        "total_anomalous_weeks": len(anomaly_set),
    })

    # Activity type summary nodes (intermediate)
    type_counts = {}
    for ag in activity_groups:
        etype = ag["_id"]["event_type"]
        type_counts[etype] = type_counts.get(etype, 0) + ag["count"]

    for etype, total_count in type_counts.items():
        type_node_id = f"type_{etype}"
        nodes.append({
            "id": type_node_id,
            "label": etype,
            "type": "activity_type",
            "total_events": total_count,
            "risk_level": "info",
        })
        links.append({
            "source": user_node_id,
            "target": type_node_id,
            "label": f"{total_count:,} events",
            "value": min(8, max(2, total_count / 10000)),
        })

    # Weekly activity nodes
    for ag in activity_groups:
        etype = ag["_id"]["event_type"]
        year = ag["_id"]["year"]
        week = ag["_id"]["week"]
        count = ag["count"]
        after_hours = ag["after_hours_count"]
        weekend = ag["weekend_count"]
        pcs = ag.get("pcs", [])

        week_key = (year, week)
        is_anomalous = week_key in anomaly_set
        recon_error = anomaly_errors.get(week_key, 0)

        # Determine risk level
        if is_anomalous and recon_error > 0.001:
            risk_level = "high"
        elif is_anomalous or after_hours > count * 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Get weekly feature context
        wf = weekly_features.get(week_key, {})

        node_id = f"{etype}_{year}_W{week}"
        nodes.append({
            "id": node_id,
            "label": f"W{week}'{str(year)[-2:]}",
            "type": "activity",
            "event_type": etype,
            "year": year,
            "week": week,
            "count": count,
            "after_hours_count": after_hours,
            "weekend_count": weekend,
            "after_hours_pct": round(after_hours / count * 100, 1) if count else 0,
            "pcs": pcs[:5],
            "risk_level": risk_level,
            "is_anomalous": is_anomalous,
            "reconstruction_error": round(recon_error, 6) if is_anomalous else None,
            "weekly_context": {
                "logon_count": wf.get("logon_count"),
                "file_events": wf.get("file_events"),
                "usb_events": wf.get("usb_events"),
                "email_events": wf.get("email_events"),
            } if wf else None,
        })

        # Link from activity type node to weekly node
        links.append({
            "source": f"type_{etype}",
            "target": node_id,
            "label": f"{count} events",
            "value": min(5, max(1, count / 50)),
            "risk_level": risk_level,
        })

    return {
        "user_id": user_id,
        "nodes": nodes,
        "links": links,
        "summary": {
            "total_events": sum(type_counts.values()),
            "total_weeks": len(set((ag["_id"]["year"], ag["_id"]["week"]) for ag in activity_groups)),
            "anomalous_weeks": len(anomaly_set),
            "risk_score": round(user_risk, 6),
            "event_types": type_counts,
        }
    }
