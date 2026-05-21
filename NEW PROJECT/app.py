"""
AI Visual Intelligence System — Streamlit Dashboard
Real-time dashboard with live video, detection overlays, and analytics panels.
"""
import sys
import os
import time
import cv2
import numpy as np
import streamlit as st
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from modules.video_capture import VideoCapture
from modules.detector import ObjectDetector
from modules.tracker import ObjectTracker
from modules.object_identifier import ObjectIdentifier
from modules.crowd_analyzer import CrowdAnalyzer
from modules.traffic_monitor import TrafficMonitor
from modules.behavior_analyzer import BehaviorAnalyzer
from modules.scene_understanding import SceneUnderstanding
from database import EventLogger
from utils.drawing import (
    draw_tracks, draw_crowd_overlay, draw_traffic_info,
    draw_violations, draw_alerts, draw_scene_caption,
    draw_fps, draw_heatmap,
)
from utils.helpers import FPSCounter, format_timestamp

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Visual Intelligence System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main { background: #0e1117; }

    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1d23 50%, #0e1117 100%);
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.3rem 0 0;
        font-size: 0.9rem;
    }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(145deg, #1e2028, #262a33);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }

    /* Alert cards */
    .alert-critical {
        background: linear-gradient(135deg, #ff4757, #ff6b81);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .alert-warning {
        background: linear-gradient(135deg, #ffa502, #ff7f50);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .alert-info {
        background: linear-gradient(135deg, #3742fa, #5f6cff);
        color: white;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Density badges */
    .density-low { color: #2ed573; font-weight: 700; }
    .density-medium { color: #ffa502; font-weight: 700; }
    .density-high { color: #ff4757; font-weight: 700; }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d23 0%, #0e1117 100%);
    }

    /* Signal indicator */
    .signal-red {
        display: inline-block;
        width: 20px; height: 20px;
        border-radius: 50%;
        background: #ff4757;
        box-shadow: 0 0 12px #ff4757;
    }
    .signal-green {
        display: inline-block;
        width: 20px; height: 20px;
        border-radius: 50%;
        background: #2ed573;
        box-shadow: 0 0 12px #2ed573;
    }

    /* Log entries */
    .log-entry {
        background: rgba(255,255,255,0.03);
        border-left: 3px solid #667eea;
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.4rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.8);
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "running": False,
        "locked_id": None,
        "violations_log": [],
        "alerts_log": [],
        "frame_count": 0,
        "show_heatmap": False,
        "scene_caption": "Waiting for scene analysis...",
        "crowd_count": 0,
        "crowd_density": "LOW",
        "fps": 0.0,
        "object_counts": {},
        "total_violations": 0,
        "total_alerts": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()


# ─── Cached Resource Loading ────────────────────────────────────
@st.cache_resource
def load_detector():
    return ObjectDetector()

@st.cache_resource
def load_tracker():
    return ObjectTracker()

@st.cache_resource
def load_modules():
    det = load_detector()
    return {
        "identifier": ObjectIdentifier(det),
        "crowd": CrowdAnalyzer(),
        "traffic": TrafficMonitor(),
        "behavior": BehaviorAnalyzer(),
        "scene": SceneUnderstanding(),
        "db": EventLogger(),
        "fps": FPSCounter(),
    }


# ─── Header ─────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔍 AI Visual Intelligence System</h1>
    <p>Real-Time Object Detection • Tracking • Behavior Analysis • Scene Understanding</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar Controls ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Controls")

    # Camera source
    source_option = st.selectbox(
        "📷 Video Source",
        ["Webcam (0)", "Webcam (1)", "Video File"],
        index=0,
    )

    video_file = None
    if source_option == "Video File":
        video_file = st.text_input("File path:", placeholder="/path/to/video.mp4")

    st.divider()

    # Model settings
    st.markdown("### 🧠 Model Settings")
    model_variant = st.selectbox("YOLO Model", ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"], index=0)
    conf_threshold = st.slider("Confidence Threshold", 0.1, 0.9, 0.45, 0.05)

    st.divider()

    # Traffic controls
    st.markdown("### 🚦 Traffic Signal")
    col_sig1, col_sig2 = st.columns(2)
    with col_sig1:
        if st.button("🔴 RED", use_container_width=True):
            modules = load_modules()
            modules["traffic"].set_signal("RED")
    with col_sig2:
        if st.button("🟢 GREEN", use_container_width=True):
            modules = load_modules()
            modules["traffic"].set_signal("GREEN")

    auto_signal = st.checkbox("Auto-cycle signal", value=True)

    st.divider()

    # Display options
    st.markdown("### 🎨 Display Options")
    show_heatmap = st.checkbox("Show Crowd Heatmap", value=False)
    show_trajectories = st.checkbox("Show Trajectories", value=True)

    st.divider()

    # Target lock
    st.markdown("### 🎯 Target Lock")
    lock_input = st.number_input("Lock Track ID:", min_value=-1, value=-1, step=1)
    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        if st.button("🔒 Lock", use_container_width=True):
            if lock_input >= 0:
                tracker = load_tracker()
                tracker.lock_target(lock_input)
                st.session_state.locked_id = lock_input
    with col_lock2:
        if st.button("🔓 Unlock", use_container_width=True):
            tracker = load_tracker()
            tracker.unlock_target()
            st.session_state.locked_id = None

    if st.session_state.locked_id is not None:
        st.success(f"🎯 Locked on ID: {st.session_state.locked_id}")


# ─── Stats Row ──────────────────────────────────────────────────
stat_cols = st.columns(6)
stat_placeholders = {}
labels = ["🎯 Objects", "👥 Crowd", "📊 Density", "🚨 Violations", "⚠️ Alerts", "⚡ FPS"]
keys = ["objects", "crowd", "density", "violations", "alerts", "fps"]
for i, (label, key) in enumerate(zip(labels, keys)):
    with stat_cols[i]:
        stat_placeholders[key] = st.empty()


def update_stat_cards(detections_count, crowd_stats, violations_count, alerts_count, fps_val):
    density_class = {
        "LOW": "density-low", "MEDIUM": "density-medium", "HIGH": "density-high"
    }.get(crowd_stats.density_level, "density-low")

    stat_placeholders["objects"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{detections_count}</div>
        <div class="stat-label">🎯 Objects Detected</div>
    </div>""", unsafe_allow_html=True)

    stat_placeholders["crowd"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{crowd_stats.count}</div>
        <div class="stat-label">👥 People Count</div>
    </div>""", unsafe_allow_html=True)

    stat_placeholders["density"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value {density_class}">{crowd_stats.density_level}</div>
        <div class="stat-label">📊 Crowd Density</div>
    </div>""", unsafe_allow_html=True)

    stat_placeholders["violations"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{violations_count}</div>
        <div class="stat-label">🚨 Total Violations</div>
    </div>""", unsafe_allow_html=True)

    stat_placeholders["alerts"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{alerts_count}</div>
        <div class="stat-label">⚠️ Behavior Alerts</div>
    </div>""", unsafe_allow_html=True)

    stat_placeholders["fps"].markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{fps_val:.1f}</div>
        <div class="stat-label">⚡ FPS</div>
    </div>""", unsafe_allow_html=True)


# ─── Main Layout ─────────────────────────────────────────────────
main_col, side_col = st.columns([3, 1])

with main_col:
    st.markdown("### 📹 Live Video Feed")
    video_placeholder = st.empty()

with side_col:
    st.markdown("### 📋 Live Events")
    scene_placeholder = st.empty()
    st.markdown("#### 🚨 Violations")
    violations_placeholder = st.empty()
    st.markdown("#### ⚠️ Alerts")
    alerts_placeholder = st.empty()
    st.markdown("#### 🏷️ Tracked Objects")
    tracks_placeholder = st.empty()


# ─── Video Processing Loop ──────────────────────────────────────
start_btn_col, stop_btn_col, _ = st.columns([1, 1, 4])
with start_btn_col:
    start = st.button("▶️ Start System", type="primary", use_container_width=True)
with stop_btn_col:
    stop = st.button("⏹ Stop", use_container_width=True)

if stop:
    st.session_state.running = False

if start:
    st.session_state.running = True

    # Determine video source
    if source_option == "Webcam (0)":
        src = 0
    elif source_option == "Webcam (1)":
        src = 1
    else:
        src = video_file if video_file else 0

    try:
        cap = VideoCapture(src)
    except RuntimeError as e:
        st.error(f"❌ Could not open video source: {e}")
        st.session_state.running = False
        st.stop()

    # Load modules
    detector = load_detector()
    tracker = load_tracker()
    modules = load_modules()

    # Update config from sidebar
    config.CONFIDENCE_THRESHOLD = conf_threshold

    if auto_signal:
        modules["traffic"].enable_auto_signal()

    fps_counter = modules["fps"]
    frame_number = 0

    while st.session_state.running:
        ret, frame = cap.read_frame()
        if not ret:
            st.warning("📷 Video feed ended or unavailable.")
            break

        frame_number += 1
        fps_counter.tick()

        # ─── Detection ─────────────────────────────────────────
        detections = detector.detect(frame)

        # ─── Tracking ──────────────────────────────────────────
        tracked = tracker.update(detections, frame)

        # ─── Analysis ──────────────────────────────────────────
        crowd_stats = modules["crowd"].analyze(tracked, frame.shape)
        violations = modules["traffic"].check_violations(tracked)
        alerts = modules["behavior"].analyze(tracked)
        caption = modules["scene"].describe(frame)

        # ─── Logging ───────────────────────────────────────────
        if frame_number % 30 == 0:
            modules["db"].log_crowd_stats(
                crowd_stats.count, crowd_stats.density_level, crowd_stats.density_value
            )

        for v in violations:
            modules["db"].log_violation(v.violation_type, v.track_id, v.details)
            st.session_state.violations_log.insert(0, {
                "time": format_timestamp(v.timestamp),
                "type": v.violation_type,
                "details": v.details,
            })
            st.session_state.total_violations += 1

        for a in alerts:
            modules["db"].log_event("ALERT", {"type": a.alert_type, "details": a.details}, frame_number)
            st.session_state.alerts_log.insert(0, {
                "time": format_timestamp(a.timestamp),
                "type": a.alert_type,
                "details": a.details,
                "severity": a.severity,
            })
            st.session_state.total_alerts += 1

        # ─── Drawing ──────────────────────────────────────────
        display = frame.copy()

        # Heatmap
        if show_heatmap and crowd_stats.heatmap is not None:
            display = draw_heatmap(display, crowd_stats.heatmap, alpha=0.35)

        # Tracked objects
        display = draw_tracks(display, tracked, st.session_state.locked_id)

        # Crowd overlay
        display = draw_crowd_overlay(display, crowd_stats)

        # Traffic
        signal = modules["traffic"].get_signal_state()
        display = draw_traffic_info(display, signal, config.STOP_LINE_Y)

        # Violations & alerts on frame
        display = draw_violations(display, violations)
        display = draw_alerts(display, alerts)

        # Scene caption
        display = draw_scene_caption(display, caption)

        # FPS
        current_fps = fps_counter.get_fps()
        display = draw_fps(display, current_fps)

        # ─── Update UI ────────────────────────────────────────
        # Convert BGR to RGB for Streamlit
        display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        video_placeholder.image(display_rgb, channels="RGB", use_container_width=True)

        # Stats
        update_stat_cards(
            len(detections), crowd_stats,
            st.session_state.total_violations,
            st.session_state.total_alerts,
            current_fps,
        )

        # Scene caption
        scene_placeholder.markdown(f"""
        <div class="alert-info">
            🧠 <strong>Scene:</strong> {caption}
        </div>
        """, unsafe_allow_html=True)

        # Violations log
        if st.session_state.violations_log:
            viol_html = ""
            for v in st.session_state.violations_log[:5]:
                viol_html += f'<div class="log-entry">🚨 <strong>{v["type"]}</strong><br>{v["details"]}<br><small>{v["time"]}</small></div>'
            violations_placeholder.markdown(viol_html, unsafe_allow_html=True)
        else:
            violations_placeholder.markdown("_No violations detected_")

        # Alerts log
        if st.session_state.alerts_log:
            alert_html = ""
            for a in st.session_state.alerts_log[:5]:
                cls = "alert-critical" if a["severity"] == "CRITICAL" else "alert-warning"
                alert_html += f'<div class="{cls}">⚠️ {a["type"]}: {a["details"]}<br><small>{a["time"]}</small></div>'
            alerts_placeholder.markdown(alert_html, unsafe_allow_html=True)
        else:
            alerts_placeholder.markdown("_No alerts_")

        # Tracked objects list
        if tracked:
            tracks_html = ""
            for t in tracked[:10]:
                locked_marker = " 🎯" if t.track_id == st.session_state.locked_id else ""
                tracks_html += f'<div class="log-entry">ID:{t.track_id}{locked_marker} — {t.class_name} ({t.confidence:.2f})</div>'
            tracks_placeholder.markdown(tracks_html, unsafe_allow_html=True)
        else:
            tracks_placeholder.markdown("_No objects tracked_")

    cap.release()
    st.session_state.running = False
    st.info("⏹ System stopped.")


# ─── Event History (shown when not running) ─────────────────────
if not st.session_state.running:
    st.divider()
    st.markdown("### 📊 Event History")

    hist_col1, hist_col2 = st.columns(2)
    with hist_col1:
        st.markdown("#### Recent Violations")
        if st.session_state.violations_log:
            for v in st.session_state.violations_log[:10]:
                st.markdown(f"🚨 **{v['type']}** — {v['details']}  \n`{v['time']}`")
        else:
            st.info("No violations recorded in this session.")

    with hist_col2:
        st.markdown("#### Recent Alerts")
        if st.session_state.alerts_log:
            for a in st.session_state.alerts_log[:10]:
                icon = "🔴" if a["severity"] == "CRITICAL" else "🟠"
                st.markdown(f"{icon} **{a['type']}** — {a['details']}  \n`{a['time']}`")
        else:
            st.info("No alerts in this session.")
