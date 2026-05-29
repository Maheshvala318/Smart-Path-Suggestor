# 🧠 Smart Path Suggestor — Full Project Analysis & Voice Agent Feature Plan

**Date**: 2026-04-09
**Methodology**: GSD (Goal → Solution → Deliverable)

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Data Flow](#2-architecture--data-flow)
3. [Component Breakdown](#3-component-breakdown)
4. [GSD Methodology Analysis](#4-gsd-methodology-analysis)
5. [Tech Stack Summary](#5-tech-stack-summary)
6. [Voice Agent Feature — Full Plan](#6-voice-agent-feature--full-plan)

---

## 1. Project Overview

**Smart Path Suggestor** is a real-time navigation assistance system designed for pedestrians (especially visually impaired users). It uses a phone's camera to detect obstacles, estimate their distance, and provide voice + vibration + visual guidance to help the user walk safely.

### What It Does (Current State)

| Capability | Description |
|-----------|-------------|
| **Object Detection** | YOLOv8n (general) + custom finetuned model (`best.pt`) for potholes, stairs, bumps |
| **Depth Estimation** | MiDaS monocular depth model converts 2D images into approximate distance (meters) |
| **Risk Scoring** | Multi-factor formula: `Risk = Weight × Proximity × VerticalMultiplier` |
| **5-Zone Navigation** | Frame split into 5 horizontal regions (-2 to +2), center = walking path |
| **Voice Guidance** | Context-aware TTS messages (e.g., "Pothole directly ahead! Stop.") |
| **Vibration Alerts** | Vibration patterns scale with danger level (CRITICAL > DANGER > WARN) |
| **Directional Audio** | Low-frequency beep (left), high-frequency beep (right) for side objects |
| **Indoor Navigation** | Step-based navigation between departments across 3 floors (notebook tool) |

---

## 2. Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     MOBILE CLIENT (Phone)                   │
│  mobile_client.html                                         │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌───────────┐  │
│  │ Camera  │→ │ Capture  │→ │ Base64     │→ │ POST to   │  │
│  │ (rear)  │  │ Frame    │  │ Encode     │  │ /detect   │  │
│  └─────────┘  └──────────┘  └────────────┘  └─────┬─────┘  │
│                                                     │       │
│  ┌───────────────────────────────────────────────────┘       │
│  │  Response:                                               │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐   │
│  │  │ Voice   │  │ Vibrate │  │ Bounding │  │ Zone     │   │
│  │  │ TTS     │  │ Pattern │  │ Boxes    │  │ Display  │   │
│  │  └─────────┘  └─────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (Laptop on WiFi)                   │
│  server.py                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐   │
│  │ Decode   │→ │ YOLO     │→ │ MiDaS Depth Estimation   │   │
│  │ Base64   │  │ Detection│  │ (3-region refinement)     │   │
│  └──────────┘  └──────────┘  └───────────┬──────────────┘   │
│                                           │                  │
│  ┌────────────────────────────────────────┘                  │
│  │  Risk Score = W × proximity × V_mult                     │
│  │  Zone Assignment → 5 horizontal + 3 vertical             │
│  │                                                           │
│  │  ┌──────────────────────────────────────────────────┐     │
│  │  │         NavigationEngine                          │     │
│  │  │  ┌───────────────┐  ┌─────────────┐              │     │
│  │  │  │ ObjectTracker │  │ ZoneSmoother │              │     │
│  │  │  │ (stability)   │  │ (hysteresis) │              │     │
│  │  │  └───────────────┘  └─────────────┘              │     │
│  │  │  ┌────────────────┐  ┌───────────────────┐       │     │
│  │  │  │ SituationState │  │ Message Builder   │       │     │
│  │  │  │ (cooldowns)    │  │ (voice sentences) │       │     │
│  │  │  └────────────────┘  └───────────────────┘       │     │
│  │  └──────────────────────────────────────────────────┘     │
│  └───────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Breakdown

### 3.1 `server.py` — Flask API Server (426 lines)

| Section | What It Does |
|---------|-------------|
| **Model Loading** | Loads 2 YOLO models + MiDaS depth model at startup |
| **Helper Functions** | `midas_to_meters()`, `get_zone()`, `get_vertical_zone()`, `get_refined_distance()` |
| **`run_detection()`** | Full pipeline: YOLO → MiDaS → per-object risk scoring → NavigationEngine |
| **Flask Routes** | `/health` (status), `/detect` (main API), `/` (serves mobile client) |
| **Server Startup** | Auto-detects WiFi IP, generates QR code for phone connection |

### 3.2 `navigation_engine.py` — Navigation Brain (607 lines)

4 classes working together:

| Class | Responsibility | Key Logic |
|-------|---------------|-----------|
| **ObjectTracker** | Stability filtering | Object must appear in 3 consecutive frames before alert |
| **ZoneSmoother** | Anti-flickering | Majority-vote over 5 frames + 60% hysteresis threshold |
| **SituationState** | Cooldown management | Prevents same message repeating (2s–10s cooldowns per level) |
| **NavigationEngine** | Orchestrator | 8-step pipeline: stabilize → smooth → threat → priority → message → speak_check → alert → direction |

**Key Design Decisions:**
- **Region-aware priority capping**: Far-side objects (±2) can never trigger CRITICAL alerts
- **High-risk escalation**: Vehicles and potholes escalate to CRITICAL at 5m instead of 3m
- **Directional beep system**: Left = low freq (400Hz), Right = high freq (800Hz)

### 3.3 `mobile_client.html` — Mobile Web App (965 lines)

| Feature | Implementation |
|---------|---------------|
| **Camera** | Rear-facing, captures at 320×240, JPEG quality 0.65 |
| **Detection Loop** | Sequential send-wait-send pattern (not parallel), 500ms interval |
| **Voice Output** | Web Speech API, CRITICAL interrupts ongoing speech |
| **Vibration** | Navigator.vibrate API, pattern-based per priority |
| **Bounding Boxes** | Canvas overlay with distance-coded colors (red/orange/yellow/green) |
| **Wake Lock** | Prevents screen sleep during navigation |
| **Responsive** | Mobile-first, desktop 3-panel layout at 1024px+ |

### 3.4 `detection_local.py` — Local Webcam Mode (131 lines)

- Standalone script using webcam (no phone needed)
- Runs YOLO + MiDaS every 8 frames for performance
- Simple beep alert via `winsound.Beep()`
- **Simpler than server pipeline** — no NavigationEngine, no zones, just distance-based beep

### 3.5 `department_navigation.ipynb` — Indoor Route Tracking

- Jupyter notebook with interactive widgets
- Tracks step counts between locations across **3 floors** (Ground, First, Second)
- 35 unique location points mapped
- Step-to-meter conversion: `1 step ≈ 0.762 meters`
- CRUD operations for routes with CSV export

### 3.6 Supporting Files

| File | Purpose |
|------|---------|
| `FORMULAS_DOCUMENTATION.md` | Complete mathematical reference for all formulas |
| `test_models.py` | API testing script for both YOLO models |
| `start_all.bat` | One-click startup script |
| `gen_cert.py` | SSL certificate generator for HTTPS |
| `best.pt` | Custom finetuned YOLO model (~19MB) |
| `department_routes.csv` | Stored route data between locations |

---

## 4. GSD Methodology Analysis

### 🎯 GOAL

| Aspect | Description |
|--------|-------------|
| **Primary Goal** | Build a real-time pedestrian navigation assistant that detects obstacles and provides multi-modal guidance (voice + vibration + visual) |
| **Target Users** | Visually impaired individuals, general pedestrians in unfamiliar environments |
| **Problem Statement** | Visually impaired users lack real-time, context-aware obstacle awareness when walking. Existing tools (white cane, guide dogs) have limited detection range and no distance estimation |
| **Success Criteria** | < 500ms detection latency, < 3m critical alert accuracy, zero false-negative rate for high-risk objects |

### 🔧 SOLUTION

| Solution Component | Technical Approach |
|--------------------|--------------------|
| **Object Detection** | YOLOv8n (80 COCO classes) + custom finetuned model for potholes, stairs, bumps |
| **Distance Estimation** | MiDaS monocular depth + 3-region vertical refinement + calibration constant |
| **Risk Assessment** | Multi-factor weighted formula: `Risk = W × proximity × V_mult` with region capping |
| **Navigation Logic** | 4-class engine: ObjectTracker → ZoneSmoother → SituationState → NavigationEngine |
| **Communication** | Client-server over WiFi, base64 frames via REST API |
| **Multi-modal Output** | Voice (TTS), vibration patterns, directional beeps, visual bounding boxes |
| **Indoor Navigation** | Pre-mapped step counts between POIs, graph-based route computation |

**Key Algorithms:**
1. **5-Zone Horizontal Segmentation** — Frame divided at 20/40/60/80% boundaries
2. **3-Zone Vertical Analysis** — Top/middle/bottom for depth refinement
3. **Stability Filtering** — 3-frame consecutive detection required
4. **Hysteresis Smoothing** — 60% majority vote over 5 frames
5. **Priority Capping** — Region-based maximum alert levels

### 📦 DELIVERABLE

| Deliverable | Status | Description |
|------------|--------|-------------|
| `server.py` | ✅ Complete | Flask API with full detection + navigation pipeline |
| `navigation_engine.py` | ✅ Complete | 4-class navigation brain with all algorithms |
| `mobile_client.html` | ✅ Complete | Responsive mobile web app with camera/voice/vibration |
| `detection_local.py` | ✅ Complete | Standalone local webcam mode |
| `department_navigation.ipynb` | ✅ Complete | Indoor step tracking tool with 35 POIs |
| `FORMULAS_DOCUMENTATION.md` | ✅ Complete | All math formulas documented |
| `best.pt` | ✅ Complete | Custom-trained YOLO model |
| **Voice Agent (Navigation)** | ❌ Planned | Voice-activated route guidance (see Section 6) |

---

## 5. Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Object Detection** | YOLOv8 (Ultralytics) | Real-time object detection |
| **Depth Estimation** | MiDaS (Intel ISL) | Monocular depth estimation |
| **Backend** | Flask + Waitress | REST API server |
| **Frontend** | Vanilla HTML/CSS/JS | Mobile web client |
| **Voice Output** | Web Speech API (SpeechSynthesis) | Text-to-speech |
| **Vibration** | Navigator.vibrate API | Haptic feedback |
| **Audio** | Web AudioContext API | Directional beeps |
| **Deep Learning** | PyTorch | MiDaS + YOLO inference |
| **Computer Vision** | OpenCV | Image processing |
| **Data Science** | Pandas, Jupyter | Route data management |

---

## 6. Voice Agent Feature — Full Plan

### 6.1 What the Voice Agent Does

A **voice-activated navigation agent** where the user speaks a command like:

> *"I want to go from Main Door to Lab 2"*

And the system:
1. **Recognizes** the speech and extracts start/end locations
2. **Computes** the optimal path (with step/meter counts per segment)
3. **Reads out** turn-by-turn directions via voice
4. **Tracks** the user's progress and announces each segment as they walk

### 6.2 GSD for Voice Agent

#### 🎯 GOAL

| Aspect | Description |
|--------|-------------|
| **Goal** | Voice-activated indoor navigation — user speaks origin + destination, system provides step-by-step walking directions |
| **Interaction** | Fully hands-free, like Google Maps voice navigation but for indoor environments |
| **Scope** | Uses existing `department_routes.csv` data (35 POIs across 3 floors) |
| **NOT in scope** | Object detection, obstacle avoidance (handled by existing pipeline) |

#### 🔧 SOLUTION

##### A. Voice Input (Speech-to-Text)

| Approach | Technology | Pros | Cons |
|----------|-----------|------|------|
| **Web Speech API** | `SpeechRecognition` (browser-native) | No install, free, works on mobile Chrome | Not reliable in noisy environments |
| **Whisper (OpenAI)** | Server-side STT | Very accurate, handles accents | Requires API key or local GPU |
| **Google Cloud STT** | Cloud API | Production-grade, Indian English support | Requires API key, costs money |

**Recommended**: Start with **Web Speech API** (free, browser-native). Upgrade to Whisper if accuracy is insufficient.

##### B. Intent Parsing (Extract Start & End)

When user says: *"I want to go from Main Door to Lab 2"*

The system needs to extract:
- **Start**: "Main Door" (Ground Floor)
- **End**: "Lab 2" (First Floor)

| Method | Description |
|--------|-------------|
| **Simple keyword matching** | Match spoken text against known location names using string similarity (Levenshtein distance or fuzzy match) |
| **Template regex** | Pattern: `"from {start} to {end}"` — extract the two location names |
| **LLM-based parsing** | Use a small LLM (e.g., Gemini Flash) to extract structured data from free-form speech |

**Recommended**: **Fuzzy keyword matching** — lightweight, no API needed, works offline.

##### C. Path Finding Algorithm

Build a **weighted graph** from `department_routes.csv`:

```
Graph Structure:
  Node = "FloorName → PointName"  (e.g., "Ground Floor → Main Door")
  Edge = Route between two points
  Weight = Steps (or meters)

Algorithm: Dijkstra's Shortest Path
  Input: start_node, end_node
  Output: ordered list of nodes + total steps/meters per segment
```

**Cross-floor handling**: Stairs and lifts act as connectors between floors.

Example output for "Main Door → Lab 2":
```
Step 1: Walk from Main Door to Stair (Ground Floor) — 25 steps (~19m)
Step 2: Climb stairs from Ground to First Floor — 40 steps (~30m)
Step 3: Walk from Stair to Lab 2 (First Floor) — 18 steps (~14m)
Total: 83 steps (~63m)
```

##### D. Voice Output (Turn-by-Turn Directions)

Use existing Web Speech API (`SpeechSynthesisUtterance`) to read out directions:

```
"Starting navigation from Main Door to Lab 2."
"Step 1: Walk 25 steps to the Staircase."
[User walks...]
"Step 2: Climb the stairs to the First Floor. 40 steps."
[User walks...]
"Step 3: Walk 18 steps to Lab 2."
"You have arrived at Lab 2."
```

##### E. User Activation Flow

```
┌──────────────┐
│  User taps   │─── "🎤" button or says wake word
│  microphone  │
└──────┬───────┘
       ▼
┌──────────────┐
│  Speech      │─── Browser SpeechRecognition API
│  Recognition │─── Converts voice → text
└──────┬───────┘
       ▼
┌──────────────┐
│  Intent      │─── Extract: start_location, end_location
│  Parser      │─── Fuzzy match against 35 known POIs
└──────┬───────┘
       ▼
┌──────────────┐
│  Path        │─── Dijkstra's algorithm on route graph
│  Finder      │─── Returns: segment list with steps/meters
└──────┬───────┘
       ▼
┌──────────────┐
│  Voice       │─── Read out each segment via TTS
│  Navigator   │─── "Walk 25 steps to the Staircase"
└──────────────┘
```

#### 📦 DELIVERABLES

| Deliverable | Type | Description |
|------------|------|-------------|
| **Route Graph Builder** | Python module | Reads `department_routes.csv` → builds NetworkX/custom graph |
| **Path Finder** | Python module | Dijkstra's shortest path → returns step-by-step segments |
| **Voice Input Handler** | JS (client-side) | Wake button + SpeechRecognition → sends text to server |
| **Intent Parser** | Python (server-side) | Fuzzy-match spoken text against known location names |
| **Voice Navigation UI** | HTML/CSS/JS | New panel in `mobile_client.html` with mic button + progress display |
| **Navigation API** | Flask endpoint | `POST /navigate` — accepts start/end text, returns route segments |
| **Complete Route Data** | CSV | All routes between all 35 POIs with measured step counts |

### 6.3 API Design

```
POST /navigate
Body: { "query": "I want to go from Main Door to Lab 2" }

Response:
{
  "success": true,
  "start": "Ground Floor → Main Door",
  "end": "First Floor → Lab 2",
  "total_steps": 83,
  "total_meters": 63.3,
  "segments": [
    {
      "step": 1,
      "instruction": "Walk from Main Door to Stair",
      "from_floor": "Ground Floor",
      "from_point": "Main Door",
      "to_floor": "Ground Floor",
      "to_point": "Stair",
      "steps": 25,
      "meters": 19.05
    },
    {
      "step": 2,
      "instruction": "Climb stairs to First Floor",
      "from_floor": "Ground Floor",
      "from_point": "Stair",
      "to_floor": "First Floor",
      "to_point": "Stair",
      "steps": 40,
      "meters": 30.48
    },
    {
      "step": 3,
      "instruction": "Walk from Stair to Lab 2",
      "from_floor": "First Floor",
      "from_point": "Stair",
      "to_floor": "First Floor",
      "to_point": "Lab 2",
      "steps": 18,
      "meters": 13.72
    }
  ],
  "voice_script": "Starting navigation. Walk 25 steps to the staircase. Then climb stairs to first floor, 40 steps. Then walk 18 steps to Lab 2. Total distance 63 meters."
}
```

### 6.4 What Needs to Be Done (Implementation Checklist)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 1 | **Complete route data collection** — Measure step counts between ALL connected POIs (currently only 1 route exists in CSV) | 🔴 High | Manual work |
| 2 | **Build route graph** — Python module that reads CSV and constructs a weighted graph | 🔴 High | ~2 hours |
| 3 | **Implement Dijkstra's shortest path** — Find optimal route between any two POIs | 🔴 High | ~1 hour |
| 4 | **Build intent parser** — Extract start/end locations from natural language text | 🟡 Medium | ~2 hours |
| 5 | **Add `/navigate` API endpoint** in `server.py` | 🟡 Medium | ~1 hour |
| 6 | **Add voice input UI** — Mic button + SpeechRecognition in `mobile_client.html` | 🟡 Medium | ~2 hours |
| 7 | **Add navigation progress UI** — Step-by-step display panel with progress bar | 🟢 Low | ~2 hours |
| 8 | **Testing & edge cases** — Missing routes, same-floor, cross-floor, invalid inputs | 🟢 Low | ~2 hours |

### 6.5 Key Consideration — Route Data Gap

> [!IMPORTANT]
> Currently, `department_routes.csv` has **only 1 route** (Main Door → Class 1, 1 step).
> For the voice agent to work, **ALL segment connections must be measured and entered**. This is the biggest blocker — the algorithm can only find paths through segments that exist in the data.

**Minimum required**: Every POI must have at least one connection to an adjacent POI, forming a connected graph. Stair/Lift nodes must bridge floors.

---

## 7. Quick Stats

| Metric | Value |
|--------|-------|
| Total Python lines | ~1,616 |
| Total HTML/JS lines | 965 |
| Total documentation lines | ~394 |
| YOLO models | 2 (yolov8n general + custom finetuned) |
| Detectable object classes | 16+ |
| Navigation POIs | 35 across 3 floors |
| Alert priority levels | 5 (CRITICAL, DANGER, WARN, GUIDE, CLEAR) |
| Horizontal zones | 5 (-2 to +2) |
| Detection latency target | < 500ms |

---

*Document generated on 2026-04-09 for Smart Path Suggestor project analysis.*
