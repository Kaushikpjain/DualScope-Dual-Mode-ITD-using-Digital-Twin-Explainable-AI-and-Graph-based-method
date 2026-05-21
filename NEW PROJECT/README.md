# 🔍 AI Visual Intelligence System

**Real-Time Object Detection, Tracking, Behavior Analysis & Scene Understanding**

An integrated AI-powered computer vision platform that processes live camera input and performs multiple advanced vision tasks in real-time.

---

## ✨ Features

| Module | Description |
|--------|-------------|
| **🎯 Object Detection** | YOLOv8-based real-time detection of 80+ object classes (COCO) |
| **🔗 Object Tracking** | DeepSORT multi-object tracking with persistent IDs and trajectories |
| **🔒 Target Locking** | Click-to-lock onto any object for continuous tracking |
| **🏷️ Object Identification** | Automatic labeling with COCO class descriptions |
| **👥 Crowd Density** | People counting, LOW/MEDIUM/HIGH classification, heatmap visualization |
| **🚦 Traffic Violations** | Stop-line crossing detection with simulated traffic signals |
| **⚠️ Suspicious Behavior** | Unattended object detection (person leaves bag behind) |
| **🧠 Scene Understanding** | Natural language scene descriptions via BLIP vision-language model |
| **📊 Event Logging** | SQLite database for violations, alerts, and crowd statistics |
| **📺 Live Dashboard** | Streamlit web UI with real-time video and analytics panels |

---

## 🏗️ Architecture

```
Camera Input → YOLOv8 Detection → DeepSORT Tracking → Analysis Modules → SQLite Logger → Streamlit Dashboard
```

### Project Structure
```
NEW PROJECT/
├── config.py                  # Global configuration
├── requirements.txt           # Python dependencies
├── main.py                    # OpenCV pipeline (development)
├── app.py                     # Streamlit dashboard (production)
├── database.py                # SQLite event logger
├── modules/
│   ├── video_capture.py       # Camera/video feed
│   ├── detector.py            # YOLOv8 detection
│   ├── tracker.py             # DeepSORT tracking
│   ├── object_identifier.py   # Object identification
│   ├── crowd_analyzer.py      # Crowd density + heatmap
│   ├── traffic_monitor.py     # Traffic violation detection
│   ├── behavior_analyzer.py   # Suspicious behavior (unattended objects)
│   └── scene_understanding.py # BLIP scene captioning
├── utils/
│   ├── drawing.py             # Visualization utilities
│   └── helpers.py             # Common helpers
├── data/
│   └── events.db              # SQLite database (auto-created)
└── README.md
```

---

## 🚀 Installation

### 1. Create Virtual Environment
```bash
cd "NEW PROJECT"
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the System

**Option A: Streamlit Dashboard (Recommended)**
```bash
streamlit run app.py
```

**Option B: OpenCV Pipeline (Development)**
```bash
python main.py
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `VIDEO_SOURCE` | `0` | Webcam index, file path, or RTSP URL |
| `YOLO_MODEL` | `yolov8n.pt` | Model variant (n/s/m/l/x) |
| `CONFIDENCE_THRESHOLD` | `0.45` | Detection confidence cutoff |
| `CROWD_THRESHOLD_LOW` | `5` | Max people for LOW density |
| `CROWD_THRESHOLD_HIGH` | `15` | Min people for HIGH density |
| `STOP_LINE_Y` | `350` | Y-coordinate of virtual stop line |
| `UNATTENDED_FRAMES_THRESH` | `90` | Frames before unattended alert (~3s) |

---

## 🎮 Controls

### Streamlit Dashboard
- **Sidebar**: Camera source, model settings, traffic signal toggle
- **Target Lock**: Enter track ID and click Lock/Unlock
- **Heatmap**: Toggle crowd density heatmap overlay

### OpenCV Window (main.py)
- **Click** on an object to lock/unlock tracking
- **T** key: Toggle traffic signal RED/GREEN
- **Q** key: Quit

---

## 📊 Datasets

| Purpose | Dataset | Source |
|---------|---------|--------|
| General Detection | COCO (80 classes) | Built-in with YOLOv8 |
| Crowd Density | ShanghaiTech | [Link](https://www.kaggle.com/datasets/tthien/shanghaitech) |
| Traffic Analysis | UA-DETRAC | [Link](https://detrac-db.rit.albany.edu/) |
| Helmet Detection | Kaggle Helmet | [Kaggle](https://www.kaggle.com/datasets/andrewmvd/helmet-detection) |
| Suspicious Behavior | UCF Crime | [Link](https://www.crcv.ucf.edu/projects/real-world/) |

---

## 🔧 Tech Stack

- **Detection**: YOLOv8 (Ultralytics) + PyTorch
- **Tracking**: DeepSORT (deep-sort-realtime)
- **Scene Captioning**: BLIP (HuggingFace Transformers)
- **Video Processing**: OpenCV
- **Dashboard**: Streamlit
- **Database**: SQLite
- **Hardware**: CUDA GPU (optional, auto-detected)

---

## 📄 License

This project is for educational and research purposes.
