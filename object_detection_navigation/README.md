# Object Detection Navigation System

This is the main Smart Path Suggestor system that provides:
- Mobile web client for navigation
- Vision-based obstacle detection with YOLO and MiDaS depth estimation
- Campus routing with Dijkstra and A* algorithm implementations

## Project Structure

```text
client/                  Mobile web client
models/                  YOLO and MiDaS model files
pathfinding_algorithms/  Campus Dijkstra and A* implementations
src/                     Main modular API, config, routing, and vision safety code
server.py                Main API entry point
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r ../requirements.txt
```

## Run Object Detection Navigation System

```bash
python server.py
```

The server starts on port `5000`, prints your local network URL, and serves:

- Mobile client: `http://<your-ip>:5000/`
- Health check: `http://<your-ip>:5000/health`
- Detection API: `POST /detect`