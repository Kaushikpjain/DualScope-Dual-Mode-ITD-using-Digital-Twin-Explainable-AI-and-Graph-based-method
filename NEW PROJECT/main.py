"""
AI Visual Intelligence System — Main Pipeline (Non-UI)
Runs all modules in a loop with OpenCV display for development / testing.
"""
import sys
import os
import time
import cv2

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
    draw_violations, draw_alerts, draw_scene_caption, draw_fps,
)
from utils.helpers import FPSCounter


def main():
    print("=" * 60)
    print("  AI Visual Intelligence System")
    print("  Real-Time Object Detection, Tracking & Analysis")
    print("=" * 60)
    print(f"  Device: {config.DEVICE}")
    print(f"  Model:  {config.YOLO_MODEL}")
    print(f"  Source: {config.VIDEO_SOURCE}")
    print("=" * 60)

    # Initialize modules
    print("[INIT] Loading video capture...")
    cap = VideoCapture()
    w, h = cap.get_resolution()
    print(f"  Resolution: {w}x{h}  FPS: {cap.get_fps():.0f}")

    print("[INIT] Loading YOLOv8 detector...")
    detector = ObjectDetector()

    print("[INIT] Initializing tracker...")
    tracker = ObjectTracker()

    print("[INIT] Initializing analysis modules...")
    identifier = ObjectIdentifier(detector)
    crowd_analyzer = CrowdAnalyzer()
    traffic_monitor = TrafficMonitor()
    traffic_monitor.enable_auto_signal(cycle_seconds=10)
    behavior_analyzer = BehaviorAnalyzer()
    scene_engine = SceneUnderstanding()

    print("[INIT] Initializing database...")
    db = EventLogger()

    fps_counter = FPSCounter()
    frame_count = 0
    locked_target_id = None

    print("\n[READY] System running. Press 'q' to quit, 't' to toggle signal, click to lock target.\n")

    # Mouse callback for target locking
    def on_mouse(event, mx, my, flags, param):
        nonlocal locked_target_id
        if event == cv2.EVENT_LBUTTONDOWN:
            for obj in param.get("tracks", []):
                x1, y1, x2, y2 = obj.bbox
                if x1 <= mx <= x2 and y1 <= my <= y2:
                    if locked_target_id == obj.track_id:
                        tracker.unlock_target()
                        locked_target_id = None
                        print(f"  [UNLOCK] Target unlocked")
                    else:
                        tracker.lock_target(obj.track_id)
                        locked_target_id = obj.track_id
                        print(f"  [LOCK] Locked onto ID:{obj.track_id} ({obj.class_name})")
                    break

    cv2.namedWindow("AI Visual Intelligence", cv2.WINDOW_NORMAL)
    callback_data = {"tracks": []}
    cv2.setMouseCallback("AI Visual Intelligence", on_mouse, callback_data)

    try:
        while True:
            ret, frame = cap.read_frame()
            if not ret:
                print("[WARN] No frame received. Retrying...")
                time.sleep(0.1)
                continue

            frame_count += 1
            fps_counter.tick()

            # ─── Detection ─────────────────────────────────────────
            detections = detector.detect(frame)

            # ─── Tracking ──────────────────────────────────────────
            tracked_objects = tracker.update(detections, frame)
            callback_data["tracks"] = tracked_objects

            # ─── Analysis ──────────────────────────────────────────
            crowd_stats = crowd_analyzer.analyze(tracked_objects, frame.shape)
            violations = traffic_monitor.check_violations(tracked_objects)
            alerts = behavior_analyzer.analyze(tracked_objects)
            caption = scene_engine.describe(frame)

            # ─── Logging (every 30 frames) ─────────────────────────
            if frame_count % 30 == 0:
                db.log_crowd_stats(crowd_stats.count, crowd_stats.density_level, crowd_stats.density_value)

            for v in violations:
                db.log_violation(v.violation_type, v.track_id, v.details)
                db.log_event("VIOLATION", {"type": v.violation_type, "track_id": v.track_id}, frame_count)
                print(f"  [VIOLATION] {v.details}")

            for a in alerts:
                db.log_event("ALERT", {"type": a.alert_type, "details": a.details}, frame_count)
                print(f"  [ALERT] {a.details}")

            # ─── Drawing ──────────────────────────────────────────
            display = frame.copy()

            # Draw tracked objects with IDs and trajectories
            display = draw_tracks(display, tracked_objects, locked_target_id)

            # Crowd overlay
            display = draw_crowd_overlay(display, crowd_stats)

            # Traffic info
            signal_state = traffic_monitor.get_signal_state()
            display = draw_traffic_info(display, signal_state, config.STOP_LINE_Y)

            # Violations
            display = draw_violations(display, violations)

            # Alerts
            display = draw_alerts(display, alerts)

            # Scene caption
            display = draw_scene_caption(display, caption)

            # FPS
            display = draw_fps(display, fps_counter.get_fps())

            # ─── Display ──────────────────────────────────────────
            cv2.imshow("AI Visual Intelligence", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('t'):
                traffic_monitor.toggle_signal()
                print(f"  [SIGNAL] Toggled to {traffic_monitor.get_signal_state()}")

    except KeyboardInterrupt:
        print("\n[STOP] Interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        db.close()
        print("[DONE] System shut down.")


if __name__ == "__main__":
    main()
