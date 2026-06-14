"""
turn_by_turn.py — Smart Turn-by-Turn Voice Navigation for Blind Users

Computes real-world directions (go straight, turn left, turn right) from
GPS coordinates along a campus path. Filters out numbered intersection
nodes and only mentions recognizable named landmarks.
"""

import math
from campus_map_data import CAMPUS_NODES, CAMPUS_EDGES


# ─── Bearing & Distance Math ────────────────────────────────────────────────

def haversine(coord1, coord2):
    """Calculate distance in meters between two GPS coordinates."""
    R = 6371000
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_bearing(coord1, coord2):
    """
    Calculate the compass bearing (0-360°) from coord1 to coord2.
    0° = North, 90° = East, 180° = South, 270° = West.
    """
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlon = lon2 - lon1

    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def get_turn_instruction(prev_bearing, next_bearing):
    """
    Compare incoming bearing vs outgoing bearing to determine the turn type.
    Returns a tuple: (instruction_text, angle_change)
    """
    angle = (next_bearing - prev_bearing + 540) % 360 - 180  # Normalize to [-180, 180]

    if -15 <= angle <= 15:
        return "Continue straight", angle
    elif 15 < angle <= 55:
        return "Bear slightly right", angle
    elif 55 < angle <= 120:
        return "Turn right", angle
    elif 120 < angle <= 165:
        return "Take a sharp right", angle
    elif -55 <= angle < -15:
        return "Bear slightly left", angle
    elif -120 <= angle < -55:
        return "Turn left", angle
    elif -165 <= angle < -120:
        return "Take a sharp left", angle
    else:
        return "Make a U-turn", angle


# ─── Node Classification ────────────────────────────────────────────────────

def is_named_location(label):
    """
    Returns True if the node is a real named place (department, gate, building).
    Returns False for numbered intersection nodes like '47', '14', '3'.
    """
    clean = label.strip()
    # Numbered nodes are purely digits
    return not clean.isdigit()


def get_landmark_side(walking_bearing, walker_coord, landmark_coord):
    """
    Determine if a landmark is 'on your left' or 'on your right'
    relative to the walking direction.
    """
    bearing_to_landmark = calculate_bearing(walker_coord, landmark_coord)
    angle_diff = (bearing_to_landmark - walking_bearing + 540) % 360 - 180

    if -15 <= angle_diff <= 15:
        return "ahead of you"
    elif angle_diff > 0:
        return "on your right"
    else:
        return "on your left"


# ─── Nearby Landmark Discovery ──────────────────────────────────────────────

def _build_adjacency():
    """Build adjacency list from CAMPUS_EDGES for neighbor lookups."""
    adj = {}
    for a, b in CAMPUS_EDGES:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    return adj


_ADJACENCY = _build_adjacency()


def find_nearby_named_landmarks(node_label, walking_bearing, walker_coord, max_distance=80):
    """
    Find named locations near a given node (especially useful for numbered
    intersection nodes). Looks at directly connected nodes and finds the
    closest named ones within max_distance meters.

    Returns list of dicts: [{"label": str, "distance": float, "side": str}]
    """
    neighbors = _ADJACENCY.get(node_label, set())
    landmarks = []

    for neighbor in neighbors:
        if is_named_location(neighbor) and neighbor in CAMPUS_NODES:
            n_coord = CAMPUS_NODES[neighbor]
            dist = haversine(walker_coord, n_coord)
            if dist <= max_distance:
                side = get_landmark_side(walking_bearing, walker_coord, n_coord)
                landmarks.append({
                    "label": neighbor,
                    "distance": round(dist, 1),
                    "side": side,
                })

    # Sort by distance — closest first
    landmarks.sort(key=lambda x: x["distance"])
    return landmarks


# ─── Main Navigation Generator ──────────────────────────────────────────────

def generate_navigation(path_labels, source_label, dest_label):
    """
    Generate smart turn-by-turn voice navigation from a list of path node labels.

    Args:
        path_labels: List of node labels in path order (e.g. ["ATAL KALAM", "47", "30", ...])
        source_label: Human-readable source name
        dest_label: Human-readable destination name

    Returns:
        dict with:
            - "instructions": list of instruction dicts
            - "voice_script": single string for TTS
            - "summary": brief summary line
    """
    if len(path_labels) < 2:
        return {
            "instructions": [],
            "voice_script": "You are already at your destination.",
            "summary": "Already at destination.",
        }

    # Get coordinates for all path nodes
    coords = []
    for label in path_labels:
        clean = ' '.join(label.strip().upper().split())
        coord = CAMPUS_NODES.get(clean)
        if not coord:
            # Try case-insensitive match
            for name, c in CAMPUS_NODES.items():
                if ' '.join(name.strip().upper().split()) == clean:
                    coord = c
                    break
        coords.append(coord)

    # Compute bearings for each segment
    bearings = []
    distances = []
    for i in range(len(path_labels) - 1):
        if coords[i] and coords[i + 1]:
            bearings.append(calculate_bearing(coords[i], coords[i + 1]))
            distances.append(haversine(coords[i], coords[i + 1]))
        else:
            bearings.append(0)
            distances.append(0)

    # Build raw instruction segments with turn detection
    raw_segments = []
    for i in range(len(path_labels) - 1):
        from_label = path_labels[i]
        to_label = path_labels[i + 1]
        current_bearing = bearings[i]
        dist = distances[i]

        # Determine turn direction at this node
        if i == 0:
            turn = "Start walking"
        else:
            prev_bearing = bearings[i - 1]
            turn, _ = get_turn_instruction(prev_bearing, current_bearing)

        # Find nearby named landmarks at the current node
        nearby = []
        if coords[i]:
            nearby = find_nearby_named_landmarks(from_label, current_bearing, coords[i])

        raw_segments.append({
            "from_label": from_label,
            "to_label": to_label,
            "distance_m": round(dist, 1),
            "steps": int(dist * 1.3),
            "turn": turn,
            "bearing": current_bearing,
            "from_is_named": is_named_location(from_label),
            "to_is_named": is_named_location(to_label),
            "nearby_landmarks": nearby,
        })

    # ── Merge and build human-friendly instructions ──
    instructions = []
    accumulated_dist = 0
    accumulated_steps = 0
    current_turn = None
    landmarks_passed = []

    for i, seg in enumerate(raw_segments):
        is_last = (i == len(raw_segments) - 1)

        # Should we start a new instruction?
        start_new = False
        if i == 0:
            start_new = True
        elif seg["turn"] not in ("Continue straight",):
            # There's an actual turn — must emit instruction
            start_new = True

        if start_new and current_turn is not None:
            # Emit the accumulated instruction
            instructions.append(_format_instruction(
                current_turn, accumulated_dist, accumulated_steps,
                landmarks_passed, is_arrival=False, dest_label=None
            ))
            accumulated_dist = 0
            accumulated_steps = 0
            landmarks_passed = []

        if start_new:
            current_turn = seg["turn"]

        accumulated_dist += seg["distance_m"]
        accumulated_steps += seg["steps"]

        # Collect any named landmarks we pass through or near
        # If the 'from' node is a named location (and not source/dest), note it
        if seg["from_is_named"] and i > 0:
            from_clean = seg["from_label"]
            if from_clean not in (source_label, dest_label):
                landmarks_passed.append({"label": from_clean, "side": "along the way"})

        # Add nearby landmarks from numbered junctions
        for lm in seg["nearby_landmarks"]:
            # Don't duplicate source/destination, don't duplicate already added
            if lm["label"] not in (source_label, dest_label):
                already = [l["label"] for l in landmarks_passed]
                if lm["label"] not in already:
                    landmarks_passed.append(lm)

        # If destination reached
        if is_last:
            instructions.append(_format_instruction(
                current_turn, accumulated_dist, accumulated_steps,
                landmarks_passed, is_arrival=True, dest_label=dest_label
            ))

    # Build total distance and steps
    total_dist = sum(s["distance_m"] for s in raw_segments)
    total_steps = sum(s["steps"] for s in raw_segments)

    # Compose the full voice script
    intro = (
        f"Starting navigation from {source_label} to {dest_label}. "
        f"Total distance is about {int(total_dist)} meters, roughly {total_steps} steps."
    )

    voice_lines = [intro]
    for inst in instructions:
        voice_lines.append(inst["speech"])

    voice_lines.append(f"You have arrived at {dest_label}.")
    voice_script = " ".join(voice_lines)

    return {
        "instructions": instructions,
        "voice_script": voice_script,
        "summary": f"{source_label} -> {dest_label}: {int(total_dist)}m, ~{total_steps} steps, {len(instructions)} directions",
        "total_distance_m": round(total_dist, 1),
        "total_steps": total_steps,
    }


def _format_instruction(turn, distance, steps, landmarks, is_arrival, dest_label):
    """
    Format a single navigation instruction into a human-friendly sentence.
    """
    dist_text = f"about {int(distance)} meters, roughly {steps} steps"

    # Build landmark mention
    landmark_text = ""
    if landmarks:
        # Pick up to 2 most relevant landmarks
        top_landmarks = landmarks[:2]
        parts = []
        for lm in top_landmarks:
            side = lm.get("side", "nearby")
            parts.append(f"{lm['label']} {side}")

        if len(parts) == 1:
            landmark_text = f" You'll pass {parts[0]}."
        else:
            landmark_text = f" You'll pass {parts[0]}, and {parts[1]}."

    if is_arrival:
        speech = f"{turn} for {dist_text}.{landmark_text}"
    else:
        speech = f"{turn} for {dist_text}.{landmark_text}"

    return {
        "turn": turn,
        "distance_m": round(distance, 1),
        "steps": steps,
        "landmarks": landmarks,
        "speech": speech,
    }


# ─── Quick Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with a known path
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pathfinding_algorithms')))

    from astar_algorithm import get_astar_paths

    test_routes = [
        ("ATAL KALAM", "DEPARTMENT OF COMPUTER SCIENCE"),
        ("GATE NO 1", "LIBRARY"),
        ("MAHATMA GANDHI GATE", "DEPARTMENT OF BOTANY"),
    ]

    for src, dst in test_routes:
        print("=" * 70)
        print(f"  ROUTE: {src}  ->  {dst}")
        print("=" * 70)

        paths_data, err = get_astar_paths(src, dst, k=1)
        if err:
            print(f"  ERROR: {err}")
            continue

        path = paths_data[0]["path"]
        print(f"  Raw path: {' -> '.join(path)}")
        print()

        result = generate_navigation(path, src, dst)

        print(f"  Summary: {result['summary']}")
        print()

        print("  🔊 VOICE NAVIGATION:")
        print(f"  {result['voice_script']}")
        print()

        for i, inst in enumerate(result["instructions"], 1):
            lm_names = [l["label"] for l in inst["landmarks"]]
            print(f"    Step {i}: {inst['turn']} | {inst['distance_m']}m | landmarks: {lm_names}")

        print()
