"""
pathfinder.py — Graph builder + Dijkstra shortest path for department navigation.
Reads floor JSON data files from data/ and builds a unified multi-floor graph.
"""

import json
import heapq
import os
from collections import defaultdict

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_floor(floor_file):
    """Load a single floor JSON and return its data."""
    with open(os.path.join(DATA_DIR, floor_file), "r") as f:
        return json.load(f)


def load_all_floors():
    """Load every floor JSON found in the data/ directory (skip cross_floor_connections)."""
    floors = {}
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.endswith(".json") and "cross_floor" not in fname:
            floor_data = load_floor(fname)
            floors[floor_data["floor_id"]] = floor_data
    return floors


def load_cross_floor_connections():
    """Load cross-floor connections if the file exists."""
    path = os.path.join(DATA_DIR, "cross_floor_connections.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f).get("connections", [])
    return []


def build_graph(floors):
    """
    Build a weighted adjacency list from floor data + cross-floor connections.
    Node key format: "FLOOR_ID::node_id" (e.g., "GF::main_door").
    Returns: (graph, node_info)
        graph     — {node_key: [(neighbor_key, distance_m, steps, note), ...]}
        node_info — {node_key: {label, x, y, type, floor_id, floor_name}}
    """
    graph = defaultdict(list)
    node_info = {}

    for floor_id, floor_data in floors.items():
        floor_name = floor_data["floor_name"]

        # Register nodes
        for nid, ndata in floor_data["nodes"].items():
            key = f"{floor_id}::{nid}"
            node_info[key] = {
                "label": ndata["label"],
                "x": ndata["x"],
                "y": ndata["y"],
                "type": ndata["type"],
                "floor_id": floor_id,
                "floor_name": floor_name,
                "node_id": nid,
            }

        # Register edges (bidirectional)
        for edge in floor_data["edges"]:
            a = f"{floor_id}::{edge['from']}"
            b = f"{floor_id}::{edge['to']}"
            d = edge["distance_m"]
            s = edge["steps"]
            note = edge.get("note", "")
            graph[a].append((b, d, s, note))
            graph[b].append((a, d, s, note))

    # Add cross-floor connections
    connections = load_cross_floor_connections()
    for conn in connections:
        a = f"{conn['floor_a']}::{conn['node_a']}"
        b = f"{conn['floor_b']}::{conn['node_b']}"
        d = conn["distance_m"]
        s = conn["steps"]
        note = conn.get("note", "")
        if a in node_info and b in node_info:
            graph[a].append((b, d, s, note))
            graph[b].append((a, d, s, note))

    return graph, node_info


def dijkstra(graph, start_key, end_key):
    """
    Dijkstra's shortest path.
    Returns: (total_distance, total_steps, path_list) or None if unreachable.
    """
    dist = {start_key: 0}
    steps = {start_key: 0}
    prev = {}
    heap = [(0, 0, start_key)]
    visited = set()

    while heap:
        d, s, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)

        if node == end_key:
            path = []
            current = end_key
            while current is not None:
                path.append(current)
                current = prev.get(current)
            path.reverse()
            return dist[end_key], steps[end_key], path

        for neighbor, edge_d, edge_s, _note in graph.get(node, []):
            new_d = d + edge_d
            if neighbor not in dist or new_d < dist[neighbor]:
                dist[neighbor] = new_d
                steps[neighbor] = s + edge_s
                prev[neighbor] = node
                heapq.heappush(heap, (new_d, s + edge_s, neighbor))

    return None


def find_node_key(node_info, query, secondary_node_info=None):
    """Fuzzy match a user query to a node key. Checks primary then secondary dict."""
    query_lower = query.strip().lower()

    # Remove common conversational fillers
    for word in ["the ", "a ", "an ", "to ", "from ", "navigate ", "go "]:
        if query_lower.startswith(word):
            query_lower = query_lower[len(word):].strip()

    # Helper for search
    def search_in_dict(info_dict):
        # 1. Match direct node ID (e.g. "1", "2")
        for key, info in info_dict.items():
            node_id = str(info.get("node_id", info.get("index", "")))
            if node_id == query_lower:
                return key

        # 2. Match exact label ignoring case
        for key, info in info_dict.items():
            if info["label"].lower() == query_lower:
                return key

        # 3. Partial match (substring)
        for key, info in info_dict.items():
            label_lower = info["label"].lower()
            if not label_lower:
                continue
            if query_lower and (query_lower in label_lower or label_lower in query_lower):
                return key
        return None

    res = search_in_dict(node_info)
    if res: return res

    if secondary_node_info:
        return search_in_dict(secondary_node_info)

    return None



def get_route_segments(path, node_info, graph):
    """Convert a path list into human-friendly route segments with directions."""
    import math
    segments = []

    for i in range(len(path) - 1):
        a_key = path[i]
        b_key = path[i + 1]
        a_info = node_info[a_key]
        b_info = node_info[b_key]

        # Calculate basic direction based on current and next segment
        direction = "straight"
        if i > 0:
            prev_key = path[i-1]
            p_info = node_info[prev_key]

            # Vectors: Segment 1 (P->A), Segment 2 (A->B)
            # Standard image coord: Y grows down
            v1 = (a_info["x"] - p_info["x"], a_info["y"] - p_info["y"])
            v2 = (b_info["x"] - a_info["x"], b_info["y"] - a_info["y"])

            # Angle of v1 and v2
            angle1 = math.atan2(v1[1], v1[0])
            angle2 = math.atan2(v2[1], v2[0])

            # Change in angle
            delta = angle2 - angle1
            # Normalize to [-pi, pi]
            while delta <= -math.pi: delta += 2*math.pi
            while delta > math.pi: delta -= 2*math.pi

            # Threshold for "straight" is ~30 degrees
            deg = math.degrees(delta)
            if deg > 30: direction = "right"
            elif deg < -30: direction = "left"
            else: direction = "straight"

            # Special case: If floors changed, it's not a horizontal turn
            if p_info["floor_id"] != a_info["floor_id"]:
                direction = "straight"

        edge_d, edge_s, edge_note = 0, 0, ""
        for neighbor, d, s, note in graph[a_key]:
            if neighbor == b_key:
                edge_d, edge_s, edge_note = d, s, note
                break

        if a_info["floor_id"] != b_info["floor_id"]:
            move = "up" if int(b_info["node_id"]) > int(a_info["node_id"]) else "down" # Rough heuristic
            # Better check floor names mapping if possible, but for now:
            instruction = f"Take {a_info['label']} from {a_info['floor_name']} to {b_info['floor_name']}"
            direction = move
        else:
            instruction = f"{a_info['label']} to {b_info['label']}"
            if edge_note:
                instruction += f" ({edge_note})"

        segments.append({
            "step": i + 1,
            "instruction": instruction,
            "direction": direction,
            "from_label": a_info["label"],
            "to_label": b_info["label"],
            "from_floor": a_info["floor_name"],
            "to_floor": b_info["floor_name"],
            "distance_m": edge_d,
            "steps": edge_s,
            "note": edge_note,
        })

    return segments


def get_all_locations(node_info):
    """Return a sorted list of all location labels grouped by floor."""
    by_floor = defaultdict(list)
    for key, info in node_info.items():
        by_floor[info["floor_name"]].append({"label": info["label"], "key": key})
    for floor in by_floor:
        by_floor[floor].sort(key=lambda x: x["label"])
    return dict(by_floor)
