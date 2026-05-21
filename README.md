<div align="center">

# 🛡️ DualScope — Dual-Mode Insider Threat Detection System

### Using Digital Twin, Explainable AI & Graph-Based Forensic Analysis

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.0-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

<p align="center">
  <em>A production-grade insider threat detection system combining unsupervised deep learning (autoencoders),<br/>
  psychometric profiling, and interactive graph-based forensic visualization.</em>
</p>

<br/>

<!-- Add your dashboard screenshot here -->
<!-- ![Dashboard Preview](screenshots/dashboard_preview.png) -->

</div>

---

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technologies Used](#-technologies-used)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [Dataset Information](#-dataset-information)
- [Model & Algorithm](#-model--algorithm)
- [Graph & Explainability](#-graph--explainability)
- [Results & Outputs](#-results--outputs)
- [Future Improvements](#-future-improvements)
- [Authors](#-authors)
- [License](#-license)

---

## 🔴 Problem Statement

Insider threats are among the most damaging and difficult-to-detect security risks facing organizations today:

| Metric | Value |
|--------|-------|
| 💰 Average annual cost of insider threats | **$15.38 million** |
| ⏱️ Average time to contain an incident | **85 days** |
| 📊 Incidents caused by negligent insiders | **56%** |
| 🔍 Harder to detect than external attacks | **Yes** |

> Traditional security systems (firewalls, IDS/IPS, antivirus) are designed against external threats and are **largely blind to insiders** who already have legitimate access. There is a critical need for intelligent behavioral analytics that can model normal behavior, detect deviations, and provide forensic investigation tools.

---

## 🔭 Project Overview

**DualScope** implements a comprehensive Insider Threat Detection System using a **Dual-Mode analytical approach**:

### 🧬 Mode 1 — Digital Twin (Behavioral Profiling)
Each employee is modeled as a **digital twin** — a mathematical representation of their normal behavioral patterns across logins, file access, USB usage, emails, and web browsing. The system detects anomalies when real activity deviates from the learned baseline using an **autoencoder neural network**.

### 🕸️ Mode 2 — Graph-Based Structural Analysis
Each user is represented as a **central node** in an interactive force-directed graph, with all activities rendered as connected nodes. Activity nodes are **color-coded by risk level** (🟢 Normal → 🟠 Suspicious → 🔴 Anomalous), enabling security analysts to visually trace behavioral patterns.

### 🧠 Explainable AI (XAI)
The system provides **feature-level contribution analysis** showing *why* a user was flagged, natural language explanations, and risk factor breakdowns — ensuring transparency for security analysts and legal compliance.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Unsupervised Anomaly Detection** | Autoencoder learns normal behavior — no labeled threat data needed |
| 🧬 **Per-User Digital Twins** | Individual behavioral baselines for each of 1,000 employees |
| 📊 **15-Dimensional Feature Vectors** | Logins, files, USB, email, HTTP, after-hours, weekend, OCEAN traits |
| 🕸️ **Interactive Graph Visualization** | Force-directed graphs with risk-colored activity nodes |
| 🧠 **Explainable AI (XAI)** | Feature deviation analysis with natural language explanations |
| 🧪 **Psychometric Integration** | Big Five personality traits (OCEAN model) enrich risk profiles |
| ⏱️ **Temporal Analysis** | Weekly feature vectors capture behavioral trends over time |
| 📈 **7-Page Interactive Dashboard** | Dashboard Hub, Digital Twin, Graph Analysis, Threats, Search, Analytics, Charts |
| 🔄 **REST API** | FastAPI backend with 9+ endpoints for real-time querying |
| 📊 **Research-Grade Evaluation** | Confusion matrix, ROC curve, F1-score against CERT ground truth |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CERT r4.2 DATASET                            │
│         (Logon · Email · File · USB · HTTP · Psychometric)          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   PREPROCESSING     │
                    │  (6 preprocessors)  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │ FEATURE ENGINEERING │
                    │  User + Weekly +    │
                    │  Temporal Features  │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼────────┐ ┌────▼─────┐ ┌────────▼────────┐
    │  AUTOENCODER ML  │ │  GRAPH   │ │  XAI ENGINE     │
    │  (Anomaly Det.)  │ │ (Network │ │  (Feature       │
    │  PyTorch · 50ep  │ │  + Page  │ │   Deviation)    │
    └─────────┬────────┘ │  Rank)   │ └────────┬────────┘
              │          └────┬─────┘          │
              └───────────────┼────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │     MONGODB       │
                    │  (6 collections)  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │   FastAPI REST    │
                    │   (9+ Endpoints)  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  REACT DASHBOARD  │
                    │   (7 Pages +      │
                    │    Recharts +     │
                    │    Force-Graph)   │
                    └───────────────────┘
```

---

## 🛠️ Technologies Used

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Language** | Python 3.12+ | Backend, ML, Data Processing |
| **Language** | JavaScript (ES6+) | Frontend Application |
| **ML Framework** | PyTorch | Autoencoder Neural Network |
| **ML Utilities** | Scikit-learn | StandardScaler, Preprocessing |
| **Backend** | FastAPI + Uvicorn | REST API Server |
| **Database** | MongoDB | NoSQL Document Store |
| **Frontend** | React 19 + Vite | Component-Based UI |
| **Visualization** | Recharts | Line, Bar, Pie, Scatter Charts |
| **Graph Viz** | react-force-graph-2d | Force-Directed Graph Rendering |
| **Network Analysis** | NetworkX | Graph Construction & PageRank |
| **Data Processing** | Pandas + PyMongo | CSV/MongoDB Data Pipelines |
| **Evaluation** | Matplotlib | Research Figures & ROC Curves |
| **Icons** | Lucide React | UI Icon Library |
| **Routing** | React Router v7 | Client-Side Navigation |
| **HTTP Client** | Axios | API Communication |

---

## 📁 Project Structure

```
DualScope/
│
├── preprocessing/                  # Step 1: Raw data cleaning
│   ├── preprocess_logon.py         #   Logon/logoff events
│   ├── preprocess_email.py         #   Email communications
│   ├── preprocess_file.py          #   File access events
│   ├── preprocess_device.py        #   USB device usage
│   ├── preprocess_http.py          #   HTTP/web browsing (streaming)
│   └── preprocess_psychometric.py  #   Big Five personality surveys
│
├── feature_engineering/            # Step 2: Behavioral features
│   ├── build_user_features.py      #   Global user-level vectors
│   ├── build_weekly_features.py    #   Weekly temporal digital twins
│   └── build_temporal_features.py  #   Time-series features
│
├── ML/                             # Step 3: Machine learning
│   ├── train_autoencoder.py        #   Train autoencoder model
│   ├── train_temporal_autoencoder.py #  Temporal autoencoder variant
│   ├── detect_anomalies.py         #   Anomaly detection (99th %ile)
│   ├── count_anomaly.py            #   Anomaly statistics
│   └── models/                     #   Saved weights (.pt, .pkl)
│       ├── temporal_ae.pt
│       └── scaler.pkl
│
├── graph/                          # Step 4: Graph construction
│   ├── build_email_graph.py        #   Email/File/USB interaction graph
│   ├── graph_anomaly.py            #   Graph anomaly analysis
│   └── data/
│       └── network_graph.json      #   Exported graph (D3-compatible)
│
├── explainability/                 # XAI module
│   └── explain_user.py             #   Feature deviation analysis
│
├── ensemble/                       # Ensemble scoring
│   └── combine_scores.py           #   Multi-signal risk aggregation
│
├── data_loader/                    # MongoDB data loaders
│   ├── load_events.py
│   ├── load_http_features.py
│   └── load_psychometric.py
│
├── backend/                        # FastAPI REST API
│   ├── main.py                     #   App entry point + CORS
│   ├── routes/
│   │   └── api.py                  #   9+ API endpoints
│   └── services/
│       └── db.py                   #   MongoDB queries & aggregations
│
├── dashboard/                      # React frontend (Vite)
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx                 #   Main app (7 pages)
│       ├── api.js                  #   Axios API client
│       ├── main.jsx                #   React entry point
│       └── index.css               #   Glassmorphism dark theme
│
├── research_figures/               # Publication-ready charts (PNG)
│
├── load_all_data.py                # Master data ingestion script
├── evaluate_detection.py           # Evaluation vs CERT ground truth
├── generate_confusion_matrix.py    # Confusion matrix generator
├── generate_roc_curve.py           # ROC curve generator
├── generate_research_charts.py     # Research paper figures
├── MATHEMATICAL_MODEL.md           # Formal mathematical documentation
├── HOW_TO_RUN.txt                  # Quick start guide
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## ⚙️ Installation

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Node.js | 18+ |
| MongoDB | 7.0+ (running on `localhost:27017`) |

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/DualScope-Insider-Threat-Detection.git
cd DualScope-Insider-Threat-Detection
```

### 2. Set Up Python Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 3. Set Up Frontend

```bash
cd dashboard
npm install
cd ..
```

### 4. Start MongoDB

```bash
# Ensure MongoDB is running on default port
mongod --dbpath /path/to/your/data
```

---

## 🚀 How to Run

### Full Pipeline (First Time Setup)

```bash
# Step 1: Preprocess raw data
cd preprocessing
python preprocess_logon.py
python preprocess_email.py
python preprocess_file.py
python preprocess_device.py
python preprocess_http.py
python preprocess_psychometric.py
cd ..

# Step 2: Feature engineering
cd feature_engineering
python build_weekly_features.py
python build_user_features.py
cd ..

# Step 3: Train ML model
cd ML
python train_autoencoder.py
cd ..

# Step 4: Detect anomalies
cd ML
python detect_anomalies.py
cd ..

# Step 5: Build graph data
cd graph
python build_email_graph.py
cd ..

# Step 6: Load all data into MongoDB
python load_all_data.py
```

### Quick Start (Data Already in MongoDB)

```bash
# Terminal 1 — Start Backend API
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Start Frontend Dashboard
cd dashboard
npm run dev
```

### Access

| Service | URL |
|---------|-----|
| 🌐 Dashboard | [http://localhost:5173](http://localhost:5173) |
| 🔧 API Server | [http://localhost:8000](http://localhost:8000) |
| 📄 API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## 📊 Dataset Information

### CERT Insider Threat Dataset (r4.2)

| Property | Value |
|----------|-------|
| **Source** | Carnegie Mellon University — Software Engineering Institute (SEI) |
| **Size** | ~14 GB (raw) |
| **Processed Events** | 3,951,531 records |
| **Users** | 1,000 employees |
| **Period** | Multi-year organizational data |
| **Ground Truth** | 70 known malicious insiders |

### Data Types

| Data Source | Description | Fields |
|-------------|-------------|--------|
| **Logon/Logoff** | Login events with timestamps | user_id, timestamp, pc, activity |
| **File Access** | File operations (copy/write/delete) | user_id, timestamp, filename, pc |
| **USB Device** | USB connect/disconnect events | user_id, timestamp, pc, activity |
| **Email** | Sent/received emails | user_id, timestamp, to, from, attachments |
| **HTTP/Web** | Web browsing activity | user_id, timestamp, url, content |
| **Psychometric** | Big Five personality surveys | user_id, O, C, E, A, N |

> ⚠️ **Note:** The raw dataset is **not included** in this repository due to its size (~14 GB). Download it from the [CERT Division](https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=508099) and place the CSV files in the `dataset/` directory.

---

## 🤖 Model & Algorithm

### Autoencoder Architecture

```
Input (15 features)
  │
  ├─ Encoder ─────────────────────────┐
  │   Linear(15 → 32) → ReLU         │
  │   Linear(32 → 16) → ReLU         │
  │                                   │
  │   Latent Space (16 dims)          │
  │                                   │
  ├─ Decoder ─────────────────────────┘
  │   Linear(16 → 32) → ReLU
  │   Linear(32 → 15)
  │
Output (15 reconstructed features)
```

### 15 Behavioral Features

| # | Feature | Source |
|---|---------|--------|
| 1 | `logon_count` | Login events |
| 2 | `after_hours_logons` | Logins outside 8AM–6PM |
| 3 | `file_events` | File access count |
| 4 | `usb_events` | USB device usage |
| 5 | `email_events` | Emails sent |
| 6 | `http_requests` | Web browsing count |
| 7 | `unique_domains` | Distinct websites visited |
| 8 | `unique_topics` | Distinct content topics |
| 9 | `after_hours_requests` | Web browsing after hours |
| 10 | `weekend_requests` | Weekend activity |
| 11–15 | `O, C, E, A, N` | Big Five personality traits |

### Anomaly Detection Logic

1. **Train** autoencoder on all 67,238 weekly feature vectors (50 epochs, MSE loss, Adam optimizer)
2. **Compute** per-sample reconstruction error: `e_i = (1/d) Σ(x_ij − x̂_ij)²`
3. **Threshold** at 99th percentile: weeks with error > τ are **anomalous**
4. **Score** users by average reconstruction error across all their weeks

### User Risk Classification

| Level | Criteria | Count |
|-------|----------|-------|
| 🔴 **CRITICAL** | ≥ 99th percentile | 10 users |
| 🟠 **HIGH** | ≥ 93rd percentile | ~57 users |
| 🟡 **MEDIUM** | ≥ 85th percentile | ~80 users |
| 🟢 **LOW** | Below 85th percentile | ~853 users |

---

## 🕸️ Graph & Explainability

### Network Graph (PageRank Centrality)

A **directed graph** is built from email, file, and USB interactions:
- **Nodes:** Users, files, devices
- **Edges:** Interactions weighted by frequency
- **Centrality:** PageRank algorithm identifies highly connected/important nodes
- **Visualization:** D3-based force-directed graph in the React dashboard

### Per-User Activity Graph

Each user gets a **forensic investigation graph**:
- 🔵 **Central node** = User
- 🟣 **Category nodes** = Activity types (LOGON, FILE, USB, EMAIL)
- 🟢🟠🔴 **Weekly nodes** = Color-coded by risk level
- Hover tooltips with event counts, after-hours %, weekend activity

### Explainable AI (XAI)

For each flagged user, the system computes:

```
Contribution(j) = |user_avg(j) − global_avg(j)| / |global_avg(j)|
```

The top 8 features with highest deviation are reported, along with:
- **Natural language explanation** of why the user was flagged
- **1–100 scaled scores** for intuitive understanding
- **Direction** (above/below organizational average)

---

## 📈 Results & Outputs

### Detection Performance

| Metric | Value |
|--------|-------|
| Total Users Monitored | 1,000 |
| Total Events Processed | 3,951,531 |
| Weekly Feature Vectors | 67,238 |
| Anomalous Weeks Detected | 673 (≈ 1%) |
| Suspicious Users | 40 |
| Confirmed Threats | 10 |

### Top 5 Highest-Risk Users

| Rank | User ID | Risk Score | Anomalous Weeks |
|------|---------|------------|-----------------|
| 1 | DLM0051 | 12.52 | 73 |
| 2 | AJF0370 | 9.24 | 57 |
| 3 | HSB0196 | 8.92 | 69 |
| 4 | LBH0942 | 7.25 | 62 |
| 5 | ATE0869 | 6.64 | 18 |

### Research Figures

<details>
<summary>📊 Click to view generated research figures</summary>

| Figure | Description |
|--------|-------------|
| `fig_top_risky_users.png` | Top 10 users — Risk Score vs Anomalous Weeks |
| `fig_activity_distribution.png` | Activity type distribution (3.9M events) |
| `fig_risk_distribution.png` | Risk score histogram with threshold zones |
| `fig_xai_contributions.png` | XAI feature deviation analysis |
| `fig_training_loss.png` | Autoencoder training loss curve |
| `fig_anomaly_timeline.png` | Weekly anomaly detection timeline |
| `fig_system_statistics.png` | System performance overview |
| `fig_approach_comparison.png` | Comparison with existing approaches |

<!-- Uncomment after adding screenshots -->
<!-- ![Dashboard](screenshots/dashboard.png) -->
<!-- ![Digital Twin](screenshots/digital_twin.png) -->
<!-- ![Graph Analysis](screenshots/graph_analysis.png) -->

</details>

---

## 🔮 Future Improvements

- [ ] **Real-Time Streaming** — Integrate Apache Kafka for live event ingestion
- [ ] **LSTM/Transformer Models** — Capture long-range temporal dependencies
- [ ] **Federated Learning** — Privacy-preserving cross-organization training
- [ ] **RBAC & Authentication** — Role-based access control for the dashboard
- [ ] **Alert System** — Email/Slack notifications for high-risk detections
- [ ] **Docker Deployment** — Containerized deployment with Docker Compose
- [ ] **Advanced Graph Analytics** — Community detection, anomalous subgraph mining
- [ ] **UEBA Integration** — Merge with User & Entity Behavior Analytics platforms
- [ ] **Adversarial Robustness** — Test against evasion attacks
- [ ] **Multi-Tenant Support** — Scale to multiple organizations

---

## 👥 Authors

| Name | Role |
|------|------|
| **Kaushik Jain** | Developer & Researcher |

<!-- Add more team members as needed -->
<!-- | **Name** | Role | -->

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### ⭐ Star this repository if you found it useful!

<br/>

Made with ❤️ for Cybersecurity Research

<br/>

[![Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/Powered%20by-PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org)
[![MongoDB](https://img.shields.io/badge/Stored%20in-MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)](https://mongodb.com)

</div>
