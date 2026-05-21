"""
AI Visual Intelligence System — Global Configuration
"""
import torch
import os

# ─── Video Source ────────────────────────────────────────────────
# 0 = default webcam, or provide a file path / RTSP URL string
VIDEO_SOURCE = 0

# ─── YOLOv8 Model ───────────────────────────────────────────────
YOLO_MODEL = "yolov8n.pt"          # nano variant for speed
CONFIDENCE_THRESHOLD = 0.45
IOU_THRESHOLD = 0.50

# ─── Device ─────────────────────────────────────────────────────
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─── Tracker ────────────────────────────────────────────────────
MAX_AGE = 30               # frames to keep a lost track alive
N_INIT = 3                 # detections before confirming a track
MAX_COSINE_DISTANCE = 0.3  # re-ID embedding distance threshold

# ─── Crowd Density ──────────────────────────────────────────────
CROWD_THRESHOLD_LOW = 5
CROWD_THRESHOLD_HIGH = 15
HEATMAP_DECAY = 0.95       # decay factor for heatmap accumulation

# ─── Traffic Monitoring ─────────────────────────────────────────
# Stop line as a horizontal line: y-coordinate in the frame
# Vehicles crossing below this y-value during RED = violation
STOP_LINE_Y = 350
RESTRICTED_ZONE = None      # (x1, y1, x2, y2) or None

# Vehicle class IDs in COCO (car=2, motorcycle=3, bus=5, truck=7)
VEHICLE_CLASSES = {2, 3, 5, 7}
PERSON_CLASS_ID = 0

# ─── Suspicious Behavior ────────────────────────────────────────
BAG_CLASSES = {24, 26, 28}  # COCO: backpack=24, handbag=26, suitcase=28
UNATTENDED_DISTANCE_THRESH = 150   # pixels — person-bag separation
UNATTENDED_FRAMES_THRESH = 90      # frames (~3 sec at 30 FPS)

# ─── Scene Understanding ────────────────────────────────────────
SCENE_MODEL = "Salesforce/blip-image-captioning-base"
SCENE_CAPTION_INTERVAL = 3.0  # seconds between captions

# ─── Database ────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "events.db")

# ─── Display ─────────────────────────────────────────────────────
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
