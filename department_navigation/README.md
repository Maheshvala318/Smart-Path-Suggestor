# Department Navigation System

This is the standalone Flask app for Department Path Finding with floor-map JSON data and turn-by-turn instructions.

## Project Structure

```text
data/          Floor map JSON files and images
templates/     HTML templates
app.py         Main Flask application
pathfinder.py  Path finding logic
turn_by_turn.py Turn-by-turn navigation instructions
```

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r ../../requirements.txt
```

## Run Department Path Finder

```bash
python app.py
```

Open `http://localhost:5050`.