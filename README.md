# Smart Path Suggestor

Smart Path Suggestor is a Python/Flask project for campus and department navigation. It includes:

- A mobile web client served by the main Flask API.
- Vision-based obstacle detection with YOLO and MiDaS depth estimation.
- Department path finding with floor-map JSON data and turn-by-turn instructions.
- Campus routing with Dijkstra and A* algorithm implementations.

## Project Structure

```text
client/                  Mobile web client
data/                    Small CSV data used by routing helpers
department_pathfinder/   Department navigation Flask app, templates, and map data
docs/                    Project documentation and diagrams
pathfinding_algorithms/  Campus Dijkstra and A* implementations
scripts/                 Helper scripts
src/                     Main modular API, config, routing, and vision safety code
server.py                Main API entry point
requirements.txt         Python dependencies
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Model Files

Large model weights are intentionally not committed to GitHub. Create a `models/` folder locally and place these files inside it:

```text
models/yolov8n.pt
models/best.pt
```

`yolov8n.pt` can be downloaded automatically by Ultralytics in many setups, or you can place a local copy in `models/`. `best.pt` is the project-trained model file.

## Run Main Mobile Vision API

```bash
python server.py
```

The server starts on port `5000`, prints your local network URL, and serves:

- Mobile client: `http://<your-ip>:5000/`
- Health check: `http://<your-ip>:5000/health`
- Detection API: `POST /detect`

## Run Department Path Finder

```bash
cd department_pathfinder
python app.py
```

Open `http://localhost:5050`.

Optional voice/LLM features use API keys loaded from a local `.env` file. Do not commit `.env`.
