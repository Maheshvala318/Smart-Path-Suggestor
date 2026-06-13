import json
import os

def generate_ground_floor():
    nodes = {
        "1": {"label": "1: Main Door", "x": 100, "y": 600, "type": "entrance"},
        "2": {"label": "2: Table", "x": 300, "y": 600, "type": "landmark"},
        "3": {"label": "3: Stair 1", "x": 300, "y": 480, "type": "stairs"},
        "4": {"label": "4: Lift", "x": 450, "y": 480, "type": "stairs"},
        "5": {"label": "5: Office Area", "x": 300, "y": 350, "type": "room"},
        
        "j1": {"label": "", "x": 225, "y": 350, "type": "corridor"}, # Junction for 6 and 7
        "6": {"label": "6: Cabin 1", "x": 225, "y": 430, "type": "room"},
        "7": {"label": "7: Cabin 2", "x": 225, "y": 270, "type": "room"},
        "8": {"label": "8: Cabin 3", "x": 150, "y": 350, "type": "room"},
        "22": {"label": "22: Washroom / Cabin", "x": 50, "y": 350, "type": "facility"},

        "9": {"label": "9: Class 1 / Meeting Room", "x": 300, "y": 220, "type": "room"},
        "10": {"label": "10: Corridor", "x": 400, "y": 220, "type": "corridor"},
        "11": {"label": "11: Class 2 (Door 1)", "x": 550, "y": 220, "type": "room"},
        "12": {"label": "12: Corridor", "x": 700, "y": 220, "type": "corridor"},
        "13": {"label": "13: Corridor", "x": 800, "y": 220, "type": "corridor"},
        "14": {"label": "14: Class 3", "x": 950, "y": 220, "type": "room"},
        "15": {"label": "15: Seminar Hall", "x": 950, "y": 350, "type": "room"},
        "16": {"label": "16: Seminar turn", "x": 1050, "y": 220, "type": "corridor"},
        "17": {"label": "17: Washroom turn", "x": 1050, "y": 160, "type": "corridor"},
        "18": {"label": "18: Water Room", "x": 1050, "y": 100, "type": "facility"},
        "19": {"label": "19: Girls Toilet", "x": 1050, "y": 40, "type": "facility"},
        "20": {"label": "20: Corridor", "x": 1150, "y": 220, "type": "corridor"},
        "21": {"label": "21: Window", "x": 1250, "y": 220, "type": "landmark"}
    }

    edges_def = [
        ("1", "2", 10, 15),
        ("2", "3", 5, 8),
        ("3", "4", 6, 9),
        ("3", "5", 6, 9),
        ("5", "9", 6, 9),
        
        ("5", "j1", 3, 4),
        ("j1", "6", 3, 4),
        ("j1", "7", 3, 4),
        ("j1", "8", 3, 4),
        ("8", "22", 4, 6),
        
        ("9", "10", 3, 5),
        ("10", "11", 5, 7),
        ("11", "12", 5, 7),
        ("12", "13", 3, 5),
        ("13", "14", 5, 7),
        ("14", "15", 10, 15),
        ("14", "16", 4, 6),
        ("16", "17", 2, 3),
        ("16", "20", 3, 5),
        ("17", "18", 2, 3),
        ("18", "19", 2, 3),
        ("20", "21", 3, 5)
    ]

    edges = []
    for f, t, d, s in edges_def:
        edges.append({
            "from": f,
            "to": t,
            "distance_m": d,
            "steps": s
        })

    data = {
        "floor_name": "Ground Floor",
        "floor_id": "GF",
        "nodes": nodes,
        "edges": edges
    }

    output_path = os.path.join("department_pathfinder", "data", "ground_floor.json")
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_ground_floor()
