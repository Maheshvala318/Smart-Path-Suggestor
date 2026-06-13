import json
import math

dots = json.load(open('red_dots.json'))

nodes_def = [
    {"id": "main_door", "label": "Main Door", "rx": 121, "ry": 662},
    {"id": "table", "label": "Table", "rx": 309, "ry": 667},
    
    {"id": "stair", "label": "Stair", "rx": 305, "ry": 517},
    {"id": "lift", "label": "Lift", "rx": 442, "ry": 485},
    
    {"id": "cabin23", "label": "Cabin 2 & 3", "rx": 159, "ry": 299},
    {"id": "cabin1", "label": "Cabin 1", "rx": 235, "ry": 303},
    {"id": "office", "label": "Office Area", "rx": 305, "ry": 297},
    
    {"id": "class1", "label": "Class 1 / Meeting Room", "rx": 306, "ry": 228},
    {"id": "class2_1", "label": "Class 2 (Door 1)", "rx": 570, "ry": 224},
    {"id": "class2_2", "label": "Class 2 (Door 2) / Class 3", "rx": 816, "ry": 222},
    {"id": "sem_turn", "label": "Seminar Hall Corridor Turn", "rx": 890, "ry": 219},
    {"id": "wash_turn", "label": "Washroom Corridor Turn", "rx": 1020, "ry": 218},
    {"id": "water_room", "label": "Water Room", "rx": 1082, "ry": 216},
    {"id": "window1", "label": "", "rx": 1149, "ry": 218}, # Unlabeled corridor dot near window
    {"id": "window2", "label": "Window", "rx": 1235, "ry": 216},
    
    {"id": "seminarhall", "label": "Seminar Hall", "rx": 1023, "ry": 449},
    
    {"id": "stair2", "label": "Stair 2", "rx": 1087, "ry": 194},
    {"id": "girls_toilet", "label": "Girls Toilet", "rx": 1082, "ry": 75},
    {"id": "boys_toilet", "label": "Boys Toilet", "rx": 890, "ry": 75} # Hardcoded approximate, might not be picked up by OpenCV
]

# Match exact
mapped_nodes = {}
for nd in nodes_def:
    # Find nearest dot
    if "rx" in nd:
        nearest = min(dots, key=lambda d: math.hypot(d['x'] - nd['rx'], d['y'] - nd['ry']))
        dist = math.hypot(nearest['x'] - nd['rx'], nearest['y'] - nd['ry'])
        if dist < 50:
            x, y = nearest['x'], nearest['y']
        else:
            x, y = nd['rx'], nd['ry'] # Use approximation if OpenCV missed it
    else:
        x, y = nd['x'], nd['y']

    if nd['id'] not in ["window1"]:
        mapped_nodes[nd['id']] = {
            "label": nd["label"],
            "x": x,
            "y": y,
            "type": "entrance" if "door" in nd['id'] else ("stairs" if "stair" in nd['id'] or "lift" in nd['id'] else ("facility" if "toilet" in nd['id'] or "water" in nd['id'] else ("corridor" if "turn" in nd['id'] else "room")))
        }

# Build edges (ONLY connecting these exact dots based on the image structure!)
# main door to table
# table to stair
# stair to lift
# stair to office
# office to cabin1, cabin1 to cabin23
# office to class1
# class1 to class2_1, to class2_2, to sem_turn, to wash_turn, to water_room, to window2
# sem_turn to boys_toilet, sem_turn down to seminarhall
# wash_turn down to stair2
# water_room to girls_toilet
edges = [
    {"from": "main_door", "to": "table", "distance_m": 11.43, "steps": 15},
    {"from": "table", "to": "stair", "distance_m": 6.1, "steps": 8},
    {"from": "stair", "to": "lift", "distance_m": 6.86, "steps": 9},
    {"from": "stair", "to": "office", "distance_m": 6.86, "steps": 9},
    
    {"from": "office", "to": "cabin1", "distance_m": 2.0, "steps": 3},
    {"from": "cabin1", "to": "cabin23", "distance_m": 4.0, "steps": 5},
    
    {"from": "office", "to": "class1", "distance_m": 5.33, "steps": 7},
    {"from": "class1", "to": "class2_1", "distance_m": 6.86, "steps": 9},
    {"from": "class2_1", "to": "class2_2", "distance_m": 18.29, "steps": 24},
    {"from": "class2_2", "to": "sem_turn", "distance_m": 4.0, "steps": 5},
    {"from": "sem_turn", "to": "wash_turn", "distance_m": 3.5, "steps": 5},
    {"from": "wash_turn", "to": "water_room", "distance_m": 2.0, "steps": 3},
    {"from": "water_room", "to": "window2", "distance_m": 4.0, "steps": 5},
    
    {"from": "sem_turn", "to": "boys_toilet", "distance_m": 2.5, "steps": 3},
    {"from": "sem_turn", "to": "seminarhall", "distance_m": 20.57, "steps": 27},
    
    {"from": "wash_turn", "to": "stair2", "distance_m": 3.0, "steps": 4},
    
    {"from": "water_room", "to": "girls_toilet", "distance_m": 3.05, "steps": 4}
]

out = {
    "floor_name": "Ground Floor",
    "floor_id": "GF",
    "nodes": mapped_nodes,
    "edges": edges
}

with open("department_pathfinder/data/ground_floor.json", "w") as f:
    json.dump(out, f, indent=2)

print("Mapping complete!")
