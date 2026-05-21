"""
Drawing Utilities
Renders bounding boxes, tracks, overlays, alerts, and heatmaps on frames.
"""
import cv2
import numpy as np
from typing import List, Optional


# ─── Color Palette (BGR) ─────────────────────────────────────────
COLORS = {
    "person":     (0, 220, 0),      # green
    "car":        (255, 150, 0),    # blue-ish
    "truck":      (255, 100, 50),
    "bus":        (255, 50, 100),
    "motorcycle": (200, 100, 255),
    "bicycle":    (100, 255, 200),
    "backpack":   (0, 200, 255),    # yellow
    "handbag":    (0, 200, 255),
    "suitcase":   (0, 200, 255),
    "default":    (200, 200, 200),  # grey
}

ALERT_COLOR = (0, 0, 255)       # red
VIOLATION_COLOR = (0, 50, 255)  # dark red
LOCKED_COLOR = (255, 0, 255)    # magenta
TRAJECTORY_COLOR = (255, 255, 0)  # cyan


def _get_color(class_name: str) -> tuple:
    return COLORS.get(class_name, COLORS["default"])


def draw_detections(frame: np.ndarray, detections, alpha: float = 0.7) -> np.ndarray:
    """Draw bounding boxes with class labels and confidence scores."""
    overlay = frame.copy()
    for det in detections:
        x1, y1, x2, y2 = det.bbox
        color = _get_color(det.class_name)
        label = f"{det.class_name} {det.confidence:.2f}"

        # Draw filled rectangle header
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.rectangle(overlay, (x1, y1 - text_size[1] - 8), (x1 + text_size[0] + 4, y1), color, -1)
        cv2.putText(overlay, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Draw bounding box
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def draw_tracks(frame: np.ndarray, tracked_objects, locked_id=None) -> np.ndarray:
    """Draw tracked object IDs and trajectory lines."""
    for obj in tracked_objects:
        x1, y1, x2, y2 = obj.bbox
        tid = obj.track_id
        is_locked = (locked_id is not None and tid == locked_id)
        color = LOCKED_COLOR if is_locked else _get_color(obj.class_name)
        thickness = 3 if is_locked else 2

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

        # ID label
        label = f"ID:{tid} {obj.class_name}"
        if is_locked:
            label = f"[LOCKED] {label}"
        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
        cv2.rectangle(frame, (x1, y1 - text_size[1] - 10), (x1 + text_size[0] + 6, y1), color, -1)
        cv2.putText(frame, label, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        # Trajectory line
        if len(obj.trajectory) > 1:
            pts = np.array(obj.trajectory, dtype=np.int32).reshape(-1, 1, 2)
            cv2.polylines(frame, [pts], False, TRAJECTORY_COLOR, 2, cv2.LINE_AA)

        # Locked target highlight
        if is_locked:
            # Corner brackets
            corner_len = 20
            cv2.line(frame, (x1, y1), (x1 + corner_len, y1), LOCKED_COLOR, 3)
            cv2.line(frame, (x1, y1), (x1, y1 + corner_len), LOCKED_COLOR, 3)
            cv2.line(frame, (x2, y1), (x2 - corner_len, y1), LOCKED_COLOR, 3)
            cv2.line(frame, (x2, y1), (x2, y1 + corner_len), LOCKED_COLOR, 3)
            cv2.line(frame, (x1, y2), (x1 + corner_len, y2), LOCKED_COLOR, 3)
            cv2.line(frame, (x1, y2), (x1, y2 - corner_len), LOCKED_COLOR, 3)
            cv2.line(frame, (x2, y2), (x2 - corner_len, y2), LOCKED_COLOR, 3)
            cv2.line(frame, (x2, y2), (x2, y2 - corner_len), LOCKED_COLOR, 3)

    return frame


def draw_crowd_overlay(frame: np.ndarray, crowd_stats) -> np.ndarray:
    """Draw crowd count and density badge."""
    h, w = frame.shape[:2]

    # Density badge colors
    badge_colors = {"LOW": (0, 200, 0), "MEDIUM": (0, 180, 255), "HIGH": (0, 0, 255)}
    color = badge_colors.get(crowd_stats.density_level, (200, 200, 200))

    # Draw badge in top-right corner
    badge_text = f"Crowd: {crowd_stats.count} | {crowd_stats.density_level}"
    text_size = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    bx = w - text_size[0] - 20
    by = 10

    cv2.rectangle(frame, (bx - 5, by), (w - 5, by + text_size[1] + 15), (0, 0, 0), -1)
    cv2.rectangle(frame, (bx - 5, by), (w - 5, by + text_size[1] + 15), color, 2)
    cv2.putText(frame, badge_text, (bx, by + text_size[1] + 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return frame


def draw_traffic_info(frame: np.ndarray, signal_state: str, stop_line_y: int = None) -> np.ndarray:
    """Draw traffic signal state and stop line."""
    h, w = frame.shape[:2]

    # Draw stop line
    if stop_line_y is not None:
        line_color = (0, 0, 255) if signal_state == "RED" else (0, 255, 0)
        cv2.line(frame, (0, stop_line_y), (w, stop_line_y), line_color, 2, cv2.LINE_AA)
        cv2.putText(frame, "STOP LINE", (10, stop_line_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, line_color, 1)

    # Traffic signal indicator
    signal_color = (0, 0, 255) if signal_state == "RED" else (0, 255, 0)
    cv2.circle(frame, (w - 30, h - 30), 18, signal_color, -1)
    cv2.circle(frame, (w - 30, h - 30), 18, (255, 255, 255), 2)
    cv2.putText(frame, signal_state, (w - 55, h - 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, signal_color, 2)

    return frame


def draw_violations(frame: np.ndarray, violations) -> np.ndarray:
    """Draw violation markers on the frame."""
    for v in violations:
        text = f"VIOLATION: {v.violation_type}"
        cv2.putText(frame, text, (10, frame.shape[0] - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, VIOLATION_COLOR, 2)
    return frame


def draw_alerts(frame: np.ndarray, alerts) -> np.ndarray:
    """Draw suspicious behavior alerts."""
    y_offset = 40
    for alert in alerts:
        color = (0, 0, 255) if alert.severity == "CRITICAL" else (0, 165, 255)
        text = f"ALERT: {alert.alert_type}"

        # Flashing background
        cv2.rectangle(frame, (5, y_offset - 20), (400, y_offset + 5), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, y_offset - 20), (400, y_offset + 5), color, 2)
        cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        y_offset += 35

    return frame


def draw_scene_caption(frame: np.ndarray, caption: str) -> np.ndarray:
    """Draw scene description at the bottom of the frame."""
    h, w = frame.shape[:2]
    text = f"Scene: {caption}"

    # Background bar
    cv2.rectangle(frame, (0, h - 35), (w, h), (0, 0, 0), -1)
    cv2.putText(frame, text, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return frame


def draw_heatmap(frame: np.ndarray, heatmap: np.ndarray, alpha: float = 0.35) -> np.ndarray:
    """Overlay a heatmap on the frame."""
    if heatmap is None:
        return frame
    if heatmap.shape[:2] != frame.shape[:2]:
        heatmap = cv2.resize(heatmap, (frame.shape[1], frame.shape[0]))
    blended = cv2.addWeighted(frame, 1 - alpha, heatmap, alpha, 0)
    return blended


def draw_fps(frame: np.ndarray, fps: float) -> np.ndarray:
    """Draw FPS counter."""
    text = f"FPS: {fps:.1f}"
    cv2.putText(frame, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    return frame
