import json
import os
from fastapi import APIRouter, HTTPException, Query
from services.db import (
    get_dashboard_summary,
    get_all_users_with_risk,
    search_users,
    get_weekly_features,
    get_anomalies,
    get_user_psychometric,
    get_user_explain,
    get_activity_distribution,
    get_top_risky_users,
    get_weekly_anomaly_trend,
    get_psychometric_risk_correlation,
    get_user_activity_graph,
)

router = APIRouter()


# ─────────────────────────────────────────────
#  Dashboard Hub
# ─────────────────────────────────────────────
@router.get("/dashboard/summary")
def dashboard_summary():
    """High-level risk overview with real counts."""
    return get_dashboard_summary()


# ─────────────────────────────────────────────
#  User List & Search
# ─────────────────────────────────────────────
@router.get("/users")
def list_users(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    """Paginated list of users ordered by risk score."""
    return get_all_users_with_risk(limit=limit, offset=offset)


@router.get("/users/search")
def user_search(q: str = Query(..., min_length=1)):
    """Search users by ID substring."""
    return search_users(q)


# ─────────────────────────────────────────────
#  User Behavior (Digital Twin)
# ─────────────────────────────────────────────
@router.get("/users/{user_id}/behavior")
def get_user_behavior(user_id: str):
    """Weekly features + anomalies for a specific user."""
    features = get_weekly_features(user_id)
    anomalies = get_anomalies(user_id)
    psychometric = get_user_psychometric(user_id)
    return {
        "user_id": user_id,
        "features": features,
        "anomalies": anomalies,
        "psychometric": psychometric,
    }


@router.get("/users/{user_id}/explain")
def get_user_explainability(user_id: str):
    """Enhanced XAI: Feature contributions, natural language explanation, risk breakdown."""
    explanation = get_user_explain(user_id)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"No data found for user {user_id}")
    return {"user_id": user_id, **explanation}


# ─────────────────────────────────────────────
#  Graph
# ─────────────────────────────────────────────
@router.get("/graph/threats")
def get_graph_threats():
    """Serve the generated network graph JSON."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "..", "graph", "data", "network_graph.json"
    )
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph data not found. Run build_email_graph.py first.")


@router.get("/graph/user/{user_id}")
def get_user_graph(user_id: str):
    """Per-user activity graph for forensic investigation."""
    result = get_user_activity_graph(user_id)
    if not result.get("nodes"):
        raise HTTPException(status_code=404, detail=f"No activity data found for user {user_id}")
    return result


# ─────────────────────────────────────────────
#  Analytics
# ─────────────────────────────────────────────
@router.get("/analytics/overview")
def analytics_overview():
    """Global analytics: activity distribution, top risky users, psychometric correlation."""
    return {
        "activity_distribution": get_activity_distribution(),
        "top_risky_users": get_top_risky_users(10),
        "psychometric_correlation": get_psychometric_risk_correlation(),
    }


@router.get("/analytics/timeline")
def analytics_timeline():
    """Weekly anomaly trend across the entire system."""
    return get_weekly_anomaly_trend()
