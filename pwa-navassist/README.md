# NavAssist PWA

A Progressive Web App that integrates your existing navigation and detection modules.

## How It Works

This PWA **does not** contain any navigation or detection logic. It simply acts as a mobile-friendly container that displays your existing Python modules via iframe.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NavAssist PWA (React)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Navigation  │  │  Detection  │  │   Status    │         │
│  │    Tab      │  │     Tab     │  │     Tab     │         │
│  │ (iframe)    │  │  (iframe)   │  │  (logs)     │         │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘         │
└─────────┼────────────────┼──────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────┐  ┌─────────────────────────────────────────┐
│ Python Flask    │  │ Python Flask + YOLO + MiDaS             │
│ localhost:5050  │  │ localhost:5000                          │
│                 │  │                                         │
│ - Dijkstra      │  │ - YOLOv8n / Best model                  │
│ - A* algorithm  │  │ - MiDaS depth estimation                │
│ - Campus GPS    │  │ - Zone-based risk calculation           │
│ - Groq Whisper  │  │ - Voice alerts                          │
│ - Deepgram TTS  │  │ - Bounding boxes on camera feed         │
│ - Floor maps    │  │                                         │
└─────────────────┘  └─────────────────────────────────────────┘
```

## Quick Start

### 1. Start Backend Servers

```bash
# Terminal 1: Navigation Server
cd department_navigation/department_pathfinder
python app.py
# → Opens on http://localhost:5050

# Terminal 2: Detection Server
cd object_detection_navigation
python server.py
# → Opens on http://localhost:5000
```

### 2. Start PWA

```bash
cd pwa-navassist
npm run dev
# → Opens on http://localhost:5173
```

### 3. Open in Browser

Navigate to `http://localhost:5173`

## What You Get

### Navigation Tab
- **Exact same UI** as `department_navigation/department_pathfinder/templates/index.html`
- Building floor maps (GF, 1F, 2F) with SVG rendering
- Gujarat University campus map with Leaflet
- Voice search with Groq Whisper
- TTS with Deepgram / gTTS
- Dijkstra pathfinding
- A* for campus routing

### Detection Tab
- **Exact same UI** as `object_detection_navigation/client/mobile_client.html`
- Real-time camera feed
- YOLO object detection (yolov8n or fine-tuned best model)
- MiDaS depth estimation
- Zone-based risk display
- Voice alerts for obstacles
- Directional beeps for side objects

### Status Tab
- Permission status (camera, mic, speaker)
- Activity log
- Server endpoint display

## Real Data Used

### Navigation (from your existing code)
- Campus GPS coordinates: `campus_map_data.py` (76 nodes)
- Floor data: `data/ground_floor.json`, `first_floor.json`, `second_floor.json`
- Pathfinding: Dijkstra for building, A* for campus
- Turn-by-turn: AI-generated via Gemini/Groq

### Detection (from your existing code)
- YOLO models: `models/yolov8n.pt`, `models/best.pt`
- MiDaS: `intel-isl/MiDaS_small` for depth
- Distance estimation: `midas_to_meters()` with calibration scale
- Safety engine: Zone-based risk calculation
- Priority weights for different object types

## API Keys

Uses the same keys from your root `.env`:
- `GROQ_API_KEY` - For Whisper STT and LLM intent parsing
- `DEEPGRAM_API_KEY` - For TTS
- `GEMINI_API_KEY` - For AI narrative generation

## Production Build

```bash
npm run build
# Output in dist/ folder
# Serve with any static file server
```

## Notes

1. **Both Python servers must be running** for the tabs to load
2. The PWA loads the **actual Flask pages** - no code duplication
3. All YOLO + MiDaS processing happens on the Python backend
4. The React app is just a mobile-friendly container

---

Built to integrate with your existing Smart Path Suggestor modules.
