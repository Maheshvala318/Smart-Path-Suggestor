"""
app.py — Standalone Flask app for Department Path Finder.
Run: python app.py
Open: http://localhost:5050
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
import requests
import io
from gtts import gTTS
import google.generativeai as genai
from groq import Groq
from pathfinder import load_all_floors, build_graph, dijkstra, find_node_key, get_route_segments, get_all_locations

# Integration of University Pathfinding Algorithms
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pathfinding_algorithms')))
try:
    from dijkstra_algorithm import get_dijkstra_path, initialize_campus_graph as init_dijkstra_graph
    from astar_algorithm import get_astar_path, initialize_campus_graph as init_astar_graph
    HAS_UNIVERSITY_ALGS = True
except ImportError:
    HAS_UNIVERSITY_ALGS = False
    print("Warning: University pathfinding modules not found.")

from campus_map_data import CAMPUS_NODES, CAMPUS_EDGES
from turn_by_turn import generate_navigation


# Load environment variables (ensure .env exists in project root or pathfinder dir)
load_dotenv()
if os.path.exists(os.path.join(os.getcwd(), '.env')):
    load_dotenv(os.path.join(os.getcwd(), '.env'))
elif os.path.exists(os.path.join(os.path.dirname(__file__), '.env')):
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
elif os.path.exists(os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'voice_demo', '.env')):
    # Fallback to voice_demo .env if available
    load_dotenv(os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'voice_demo', '.env'))

app = Flask(__name__)

# Load graph at startup
floors = load_all_floors()
graph, node_info = build_graph(floors)

# Load campus graph if available
campus_graph = None
campus_node_info = {}
if HAS_UNIVERSITY_ALGS:
    try:
        # Use A* graph as default for campus pathfinding
        campus_graph_obj = init_astar_graph()
        campus_graph = campus_graph_obj
        for i, label in enumerate(campus_graph_obj.vertex_data):
            if label:
                cleaned_label = ' '.join(label.strip().split())
                campus_node_info[f"CAMPUS::{i}"] = {
                    "label": cleaned_label,
                    "index": i,
                    "type": "campus_node"
                }
    except Exception as e:
        print(f"Error initializing campus graph: {e}")

@app.route('/api/campus-map-data')
def api_campus_map_data():
    """Returns GPS coordinates and edges for the campus map."""
    return jsonify({
        "nodes": CAMPUS_NODES,
        "edges": CAMPUS_EDGES
    })



@app.route("/")
def index():
    locations = get_all_locations(node_info)
    if campus_node_info:
        locations["Gujarat University Campus"] = [
            {"label": info["label"], "key": key} for key, info in campus_node_info.items()
        ]
        locations["Gujarat University Campus"].sort(key=lambda x: x["label"])

    prefill = {
        "source": request.args.get("source", ""),
        "destination": request.args.get("destination", "")
    }
    return render_template("index.html", locations=locations, prefill=prefill)


@app.route("/api/locations")
def api_locations():
    locations = get_all_locations(node_info)
    if campus_node_info:
        locations["Gujarat University Campus"] = [
            {"label": info["label"], "key": key} for key, info in campus_node_info.items()
        ]
        locations["Gujarat University Campus"].sort(key=lambda x: x["label"])
    return jsonify(locations)



@app.route("/api/find-path", methods=["POST"])
def api_find_path():
    data = request.get_json()
    source = data.get("source", "").strip()
    destination = data.get("destination", "").strip()
    source_key = data.get("source_key", "").strip()
    destination_key = data.get("destination_key", "").strip()

    if not (source_key or source) or not (destination_key or destination):
        return jsonify({"error": "Both source and destination are required."}), 400

    # Try finding keys in both department and campus maps
    start_key = source_key if (source_key in node_info or source_key in campus_node_info) else find_node_key(node_info, source, campus_node_info)
    end_key = destination_key if (destination_key in node_info or destination_key in campus_node_info) else find_node_key(node_info, destination, campus_node_info)

    if not start_key:
        return jsonify({"error": f"Could not find location: '{source or source_key}'"}), 404
    if not end_key:
        return jsonify({"error": f"Could not find location: '{destination or destination_key}'"}), 404
    if start_key == end_key:
        return jsonify({"error": "Source and destination are the same."}), 400

    # ROUTING LOGIC
    # Case 1: Both are Campus Nodes
    if start_key.startswith("CAMPUS::") and end_key.startswith("CAMPUS::"):
        if not HAS_UNIVERSITY_ALGS:
            return jsonify({"error": "University algorithms not available."}), 500

        src_label = campus_node_info[start_key]["label"]
        dst_label = campus_node_info[end_key]["label"]

        from astar_algorithm import get_astar_paths
        paths_data, err = get_astar_paths(src_label, dst_label, k=3)
        if err or not paths_data:
            return jsonify({"error": err or "No path found"}), 404

        primary_path = paths_data[0]
        total_dist = primary_path["distance"]
        total_steps = primary_path["steps"]
        path_labels = primary_path["path"]

        # Generate smart turn-by-turn navigation
        nav_result = generate_navigation(path_labels, src_label, dst_label)

        # Convert turn-by-turn instructions to segments for UI
        segments = []
        for i, inst in enumerate(nav_result["instructions"]):
            lm_names = [lm["label"] for lm in inst.get("landmarks", [])]
            note = ""
            if lm_names:
                note = "Near: " + ", ".join(lm_names[:2])
            segments.append({
                "step": i + 1,
                "instruction": inst["speech"],
                "direction": inst["turn"],
                "from_label": "",
                "to_label": "",
                "from_floor": "Campus",
                "to_floor": "Campus",
                "distance_m": inst["distance_m"],
                "steps": inst["steps"],
                "note": note,
            })

        def enrich_path(labels):
            enriched = []
            for lab in labels:
                clean_lab = ' '.join(str(lab).strip().upper().split())
                coords = CAMPUS_NODES.get(clean_lab)
                if not coords:
                    for c_name, c_coords in CAMPUS_NODES.items():
                        if ' '.join(str(c_name).strip().upper().split()) == clean_lab:
                            coords = c_coords
                            break
                if coords:
                    enriched.append({"label": clean_lab, "lat": coords[0], "lon": coords[1]})
                else:
                    enriched.append({"label": clean_lab})
            return enriched

        path_nodes_with_coords = enrich_path(path_labels)

        alt_paths = []
        for p in paths_data[1:]:
            alt_paths.append(enrich_path(p["path"]))

        return jsonify({
            "success": True,
            "source": src_label,
            "destination": dst_label,
            "total_distance_m": nav_result["total_distance_m"],
            "total_steps": nav_result["total_steps"],
            "segments": segments,
            "path_nodes": path_nodes_with_coords,
            "alt_paths": alt_paths,
            "path_edges": [],
            "voice_script": nav_result["voice_script"],
            "nav_instructions": nav_result["instructions"],
            "mode": "campus",
            "is_campus": True
        })

    # Case 2: One is Campus, One is Department
    if (start_key.startswith("CAMPUS::") or end_key.startswith("CAMPUS::")):
        # Note: We could link them via "DEPARTMENT OF COMPUTER SCIENCE" if we knew which node_id that is
        return jsonify({"error": "Inter-map navigation (Campus to Department) is not fully linked yet. Please stay within one map."}), 400

    # Case 3: Both are Department Nodes (Existing logic)
    result = dijkstra(graph, start_key, end_key)
    if result is None:
        return jsonify({"error": "No path found between these locations in the department."}), 404

    total_dist, total_steps, path = result
    segments = get_route_segments(path, node_info, graph)

    path_nodes = []
    for key in path:
        info = node_info[key]
        path_nodes.append({
            "key": key,
            "label": info["label"],
            "x": info["x"],
            "y": info["y"],
            "floor_id": info["floor_id"],
        })

    path_edges = []
    for i in range(len(path) - 1):
        a = node_info[path[i]]
        b = node_info[path[i + 1]]
        path_edges.append({
            "x1": a["x"], "y1": a["y"],
            "x2": b["x"], "y2": b["y"],
            "from_floor": a["floor_id"],
            "to_floor": b["floor_id"],
        })

    return jsonify({
        "success": True,
        "source": node_info[start_key]["label"],
        "destination": node_info[end_key]["label"],
        "total_distance_m": round(total_dist, 1),
        "total_steps": total_steps,
        "segments": segments,
        "path_nodes": path_nodes,
        "path_edges": path_edges,
        "voice_script": _build_voice_script(segments, total_steps, total_dist),
        "mode": "department",
        "is_campus": False
    })



@app.route("/api/graph-data")
def api_graph_data():
    """Return all nodes and edges for rendering the full map."""
    all_nodes = []
    for key, info in node_info.items():
        all_nodes.append({
            "key": key,
            "label": info["label"],
            "x": info["x"],
            "y": info["y"],
            "type": info["type"],
            "floor_id": info["floor_id"],
            "floor_name": info["floor_name"],
        })

    all_edges = []
    seen = set()
    for floor_id, floor_data in floors.items():
        for edge in floor_data["edges"]:
            edge_key = (floor_id, tuple(sorted([edge["from"], edge["to"]])))
            if edge_key not in seen:
                seen.add(edge_key)
                a = node_info.get(f"{floor_id}::{edge['from']}")
                b = node_info.get(f"{floor_id}::{edge['to']}")
                if a and b:
                    all_edges.append({
                        "x1": a["x"], "y1": a["y"],
                        "x2": b["x"], "y2": b["y"],
                        "floor_id": floor_id,
                        "distance_m": edge["distance_m"],
                        "steps": edge["steps"],
                    })

    return jsonify({"nodes": all_nodes, "edges": all_edges})


# Simple in-memory cache for voice intents
INTENT_CACHE = {}

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return Groq(api_key=api_key)
    return None

@app.route("/api/speech-to-text", methods=["POST"])
def api_speech_to_text():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio data received"}), 400

    client = get_groq_client()
    if not client:
        return jsonify({"error": "GROQ_API_KEY not configured"}), 500

    audio_file = request.files['audio']
    try:
        # Transcribe using Whisper on Groq
        transcription = client.audio.transcriptions.create(
            file=("speech.webm", audio_file.read()),
            model="whisper-large-v3",
            response_format="json",
        )
        return jsonify({"text": transcription.text})
    except Exception as e:
        print(f"STT Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/parse-intent", methods=["POST"])
def api_parse_intent():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # 1. Check Cache
    if text in INTENT_CACHE:
        return jsonify(INTENT_CACHE[text])

    # 2. Local Regex Fallback (Save Quota)
    # Handle patterns like "X to Y", "from X to Y", "navigate to Y from X"
    import re

    # Try "from X to Y" or "X to Y"
    match = re.search(r"(?:from\s+)?(.+?)\s+to\s+(.+)", text, re.IGNORECASE)
    if not match:
        # Try "navigate to Y from X"
        match = re.search(r"navigate\s+to\s+(.+?)\s+from\s+(.+)", text, re.IGNORECASE)
        if match:
            # Swap match groups for "destination from source" pattern
            dst_raw, src_raw = match.groups()
        else:
            src_raw, dst_raw = None, None
    else:
        src_raw, dst_raw = match.groups()

    if src_raw or dst_raw:
        src_raw = src_raw.strip() if src_raw else None
        dst_raw = dst_raw.strip() if dst_raw else None

        src_found = find_node_key(node_info, src_raw, campus_node_info) if src_raw else None
        dst_found = find_node_key(node_info, dst_raw, campus_node_info) if dst_raw else None

        print(f"Local Match Check: '{src_raw}'->{src_found}, '{dst_raw}'->{dst_found}", flush=True)

        if src_found and dst_found:
            # Map back to label from appropriate dict
            src_lbl = node_info[src_found]["label"] if src_found in node_info else campus_node_info[src_found]["label"]
            dst_lbl = node_info[dst_found]["label"] if dst_found in node_info else campus_node_info[dst_found]["label"]

            res = {
                "source": src_lbl,
                "destination": dst_lbl,
                "raw_text": text,
                "method": "local_regex"
            }
            print(f"Local Match SUCCESS: {res}", flush=True)
            INTENT_CACHE[text] = res
            return jsonify(res)

        # If we have any raw input that didn't match locally, fall through to LLMs
        print("Local match incomplete. Falling through to LLM.", flush=True)

    # 3. Gemini API (If local fallback fails)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Get valid labels for matching
            labels = [info["label"] for info in node_info.values()]
            if campus_node_info:
                labels += [info["label"] for info in campus_node_info.values()]

            prompt = f"""
            Extract the navigation source and destination from the user's request.
            USER REQUEST: "{text}"
            VALID LOCATIONS:
            {", ".join(labels)}
            INSTRUCTIONS:
            1. Match the mentioned 'source' and 'destination' to the closest item in the VALID LOCATIONS list above.
            2. Use semantic meaning (e.g., "entrance" -> "1: Main Door").
            3. If not found, use an empty string.
            4. Return ONLY a valid JSON object with 'source' and 'destination' keys.
            """

            response = model.generate_content(prompt)
            content = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)

            res = {
                "source": result.get("source", ""),
                "destination": result.get("destination", ""),
                "raw_text": text,
                "method": "gemini"
            }
            INTENT_CACHE[text] = res
            return jsonify(res)
        except Exception as gemini_err:
            print(f"Gemini Error: {gemini_err}")
            # Fall through to Groq if Gemini fails (e.g. Rate Limit)

    # 4. Groq LLM Fallback (If Gemini fails or is not provided)
    client = get_groq_client()
    if client:
        try:
            labels = [info["label"] for info in node_info.values()]
            if campus_node_info:
                labels += [info["label"] for info in campus_node_info.values()]

            prompt = f"""
            Extract the navigation source and destination from the user's request.
            USER REQUEST: "{text}"
            VALID LOCATIONS:
            {", ".join(labels)}
            INSTRUCTIONS:
            1. Match the mentioned 'source' and 'destination' to the closest item in the VALID LOCATIONS list.
            2. Use semantic meaning.
            3. Return ONLY a valid JSON object with 'source' and 'destination' keys.
            """
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            result = json.loads(chat_completion.choices[0].message.content)
            res = {
                "source": result.get("source", ""),
                "destination": result.get("destination", ""),
                "raw_text": text,
                "method": "groq_llm"
            }
            INTENT_CACHE[text] = res
            return jsonify(res)
        except Exception as groq_err:
            print(f"Groq Error: {groq_err}")
            return jsonify({"error": f"Both Gemini and Groq failed: {groq_err}"}), 500

    return jsonify({"error": "No LLM service (Gemini/Groq) available or rate limited."}), 500


@app.route("/api/generate-narrative", methods=["POST"])
def api_generate_narrative():
    data = request.json
    segments = data.get("segments", [])
    total_steps = data.get("total_steps", 0)
    total_dist = data.get("total_meters", 0)

    if not segments:
        return jsonify({"error": "No segments provided"}), 400

    # Group consecutive straight segments for brevity
    grouped_segments = []
    if segments:
        current = segments[0].copy()
        landmarks = []
        for i in range(1, len(segments)):
            seg = segments[i]
            if seg["direction"] == "straight" and current["direction"] == "straight" and current["to_floor"] == seg["from_floor"]:
                # Add current to_label as a landmark we just passed
                if current["to_label"] not in landmarks:
                    landmarks.append(current["to_label"])

                # Combine
                current["steps"] += seg["steps"]
                current["distance_m"] += seg["distance_m"]
                current["to_label"] = seg["to_label"]
                current["to_floor"] = seg["to_floor"]
                if seg.get("note"):
                    current["note"] = (current.get("note", "") + "; " + seg["note"]).strip("; ")
            else:
                current["landmarks_passed"] = landmarks
                grouped_segments.append(current)
                current = seg.copy()
                landmarks = []
        current["landmarks_passed"] = landmarks
        grouped_segments.append(current)

    # Summarize segments for LLM
    route_summary = []
    for s in grouped_segments:
        landmarks_text = f" (pass {', '.join(s['landmarks_passed'])})" if s.get("landmarks_passed") else ""
        route_summary.append(f"- From {s['from_label']} to {s['to_label']}: {s['direction'].upper()}, {s['steps']} steps, {s['distance_m']}m{landmarks_text}. {s.get('note','')}")

    prompt = f"""
    Act as a smart and concise building navigation guide. Convert the following technical route data into a natural-sounding, helpful script for someone walking.

    CRITICAL INSTRUCTIONS:
    1. BE CONCISE. Don't be too wordy. Use a smart, human-to-human directing style.
    2. Focus on TURNS (Left/Right) and key landmarks.
    3. Group straight paths into single instructions (e.g., "Go straight for 50 steps past [Landmark A] then turn left").
    4. Mention step counts and landmarks naturally (e.g., "Walk about 20 steps until you see Class 1").
    5. If there is a floor change (UP/DOWN), mention the stairs/lift clearly.
    6. Return ONLY the narrative script as a plain string. No preamble.

    ROUTE DATA:
    - Total Distance: {total_dist} meters
    - Total Steps: {total_steps}
    - Total Locations: {len(segments) + 1}

    SEGMENTS:
    {chr(10).join(route_summary)}
    """

    # Try Gemini first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            narrative = response.text.strip()
            return jsonify({"narrative": narrative})
        except Exception as e:
            print(f"Gemini Narrative Error: {e}")

    # Fallback to Groq
    client = get_groq_client()
    if client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            narrative = chat_completion.choices[0].message.content.strip()
            return jsonify({"narrative": narrative})
        except Exception as e:
            print(f"Groq Narrative Error: {e}")

    # Final Local Fallback
    narrative = _build_voice_script(segments, total_steps, total_dist)
    return jsonify({"narrative": narrative})


def _build_voice_script(segments, total_steps, total_dist):
    lines = ["Starting navigation."]
    for seg in segments:
        note_part = f" {seg['note']}." if seg.get("note") else ""
        lines.append(f"Step {seg['step']}: {seg['instruction']}. {seg['steps']} steps, about {seg['distance_m']} meters.{note_part}")
    lines.append(f"You have arrived. Total: {total_steps} steps, {round(total_dist, 1)} meters.")
    return " ".join(lines)

@app.route("/api/tts", methods=["POST"])
def api_tts():
    data = request.json
    text = data.get("text", "")
    model = data.get("model", "aura-athena-en")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        api_key = os.environ.get("DEEPGRAM")

    if not api_key:
        return jsonify({"error": "Deepgram API key not configured"}), 500

    url = f"https://api.deepgram.com/v1/speak?model={model}"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"text": text}, stream=True)
        if response.status_code == 200:
            return Response(response.iter_content(chunk_size=1024), content_type="audio/mpeg")
        else:
            return jsonify({"error": f"Deepgram API error: {response.status_code}", "details": response.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tts-gtts", methods=["POST"])
def api_tts_gtts():
    data = request.json
    text = data.get("text", "")
    tld = data.get("tld", "co.in")  # co.in = Indian accent
    lang = data.get("lang", "en")
    slow = data.get("slow", False)

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        tts = gTTS(text=text, lang=lang, tld=tld, slow=slow)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return Response(audio_buffer.read(), content_type="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 50)
    print("  🏫 Department Path Finder")
    print("  Open: http://localhost:5050")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5050, debug=True)
