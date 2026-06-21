# 🎥 AI Video Intelligence Platform

A real-time AI-powered surveillance system that detects, tracks, and monitors objects across live video feeds, triggers instant zone-intrusion alerts, and visualizes everything on a live web dashboard.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-18-61DAFB)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 Overview

This project simulates a real-world smart surveillance system. It captures live video from a webcam or IP camera, runs real-time object detection and tracking using YOLOv8, monitors restricted zones for intrusions, and streams alerts to a React dashboard in real time via WebSockets — with every incident logged to a database.

Built to demonstrate end-to-end skills across **computer vision, real-time AI inference, backend API design, and full-stack system architecture**.

---

## ✨ Features

- 🎯 **Real-time object detection** — YOLOv8-powered detection across 80 COCO object classes
- 🧭 **Multi-object tracking** — persistent object IDs across frames using ByteTrack
- 🚧 **Zone / intrusion detection** — define restricted zones and get instant alerts on entry
- 📸 **Automatic snapshot capture** — saves an image whenever an alert triggers
- 📧 **Email notifications** — sends alert emails with snapshot attachments
- 🔌 **Live WebSocket alerts** — real-time push to the dashboard, no polling
- 📊 **Analytics dashboard** — live incident feed, detection charts, full history table
- 🗄️ **Incident history** — every detection event persisted to a database with timestamp, confidence, and bounding box

---

## 🏗️ Architecture

```
Webcam / IP Camera
        │
        ▼
┌───────────────────────┐
│   AI Processing Core   │   Python · OpenCV · YOLOv8 · ByteTrack
│  detect → track → zone │
└───────────┬───────────┘
            │ REST + WebSocket
            ▼
┌───────────────────────┐
│   FastAPI Backend      │   REST API · WebSocket broadcast · SQLite/PostgreSQL
└───────────┬───────────┘
            │ WebSocket + REST
            ▼
┌───────────────────────┐
│   React Dashboard       │   Live feed · Real-time alerts · Analytics charts
└───────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Computer Vision | YOLOv8 (Ultralytics), OpenCV, PyTorch |
| Object Tracking | ByteTrack |
| Backend API | FastAPI, WebSockets, SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (production-ready) |
| Frontend | React, Vite, Recharts, Axios, lucide-react |
| Notifications | SMTP (Gmail) email alerts |
| Deployment | Docker, docker-compose |

---

## 📂 Project Structure

```
ai-video-platform/
├── ai_core/                 # AI detection, tracking, and zone monitoring
│   ├── detector.py          # YOLOv8 object detection
│   ├── tracker.py           # ByteTrack object tracking
│   ├── zone_monitor.py      # Zone intrusion detection + snapshots
│   └── main.py               # Entry point — runs the live AI pipeline
├── backend/                  # FastAPI backend
│   ├── main.py
│   ├── database.py           # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── routers/               # cameras, incidents, alerts (WebSocket)
│   └── services/               # email alert service
├── frontend/                  # React dashboard
│   └── src/App.jsx
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A webcam (or RTSP camera stream)

### 1. Clone the repository
```bash
git clone https://github.com/Amaldaskm7736/ai-video-intelligence-platform.git
cd ai-video-platform
```

### 2. Set up the Python environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the project root:
```
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=your_gmail@gmail.com
```

### 4. Run the backend
```bash
cd backend
uvicorn main:app --reload --port 8000 --ws websockets
```

### 5. Run the AI core
```bash
cd ai_core
python main.py
```

### 6. Run the frontend
```bash
cd frontend
npm install
npm run dev
```

Open the dashboard at **http://localhost:5173**

---

## 📸 Screenshots

> _Add your own screenshots here — dashboard view, webcam detection window, and alert email._

| Live Dashboard | Zone Detection | Alert Email |
|---|---|---|
| _screenshot here_ | _screenshot here_ | _screenshot here_ |

---

## 🗺️ Roadmap

- [x] Real-time object detection
- [x] Multi-object tracking
- [x] Zone / intrusion detection
- [x] FastAPI backend with REST + WebSocket
- [x] React analytics dashboard
- [x] Email alerts with snapshots
- [ ] Multi-camera support
- [ ] Docker Compose deployment
- [ ] PostgreSQL production database
- [ ] GPU-accelerated inference

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙋 Author

Built by **Amaldas K M** as a portfolio project demonstrating real-time computer vision and full-stack engineering.

[LinkedIn](https://www.linkedin.com/in/amaldaskm) · [Email](mailto:amaldaskizhakkekara@gmail.com)
