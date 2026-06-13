import json

# Visual coordinates (approximate from image to look perfect)
# y positions
Y_CORR = 150
Y_OFFICE = 250
Y_STAIR = 400
Y_BOTTOM = 600

# x positions for Vertical Line
X_VERT = 200

nodes = {
    "main_door": {"label": "Main Door", "x": 100, "y": Y_BOTTOM, "type": "entrance"},
    "table": {"label": "Table", "x": X_VERT, "y": Y_BOTTOM, "type": "landmark"},
    
    "stair1": {"label": "Stair Case 1", "x": X_VERT, "y": Y_STAIR, "type": "stairs"},
    "lift": {"label": "Lift", "x": 350, "y": Y_STAIR, "type": "stairs"},
    
    "cabin3": {"label": "Cabin 3 / Washroom", "x": 50, "y": Y_OFFICE, "type": "room"},
    "cabin2": {"label": "Cabin 2", "x": 100, "y": Y_OFFICE, "type": "room"},
    "cabin1": {"label": "Cabin 1", "x": 150, "y": Y_OFFICE, "type": "room"},
    "office": {"label": "Office Area", "x": X_VERT, "y": Y_OFFICE, "type": "room"},
    
    "class1": {"label": "Classroom 1", "x": X_VERT, "y": Y_CORR, "type": "room"},
    "meeting": {"label": "Meeting Room", "x": X_VERT + 30, "y": Y_CORR, "type": "room"},
    "class2_1": {"label": "Classroom 2 (first door)", "x": 400, "y": Y_CORR, "type": "room"},
    "class2_2": {"label": "Classroom 2 (second door)", "x": 600, "y": Y_CORR, "type": "room"},
    "class3": {"label": "Classroom 3", "x": 700, "y": Y_CORR, "type": "room"},
    
    "sem_turn": {"label": "Seminar Hall Corridor Turn", "x": 850, "y": Y_CORR, "type": "corridor"},
    "wash_turn": {"label": "Washroom Corridor Turn", "x": 950, "y": Y_CORR, "type": "corridor"},
    "water_room": {"label": "Water Room", "x": 1050, "y": Y_CORR, "type": "facility"},
    "stair2": {"label": "Stair Case 2", "x": 1150, "y": Y_CORR, "type": "stairs"},
    "window": {"label": "Window", "x": 1250, "y": Y_CORR, "type": "landmark"},
    
    "seminar": {"label": "Seminar Hall", "x": 850, "y": 400, "type": "room"},
    "boys": {"label": "Boys Toilet", "x": 950, "y": 50, "type": "facility"},
    "girls": {"label": "Girls Toilet", "x": 1150, "y": 50, "type": "facility"}
}

edges = [
    {"from": "main_door", "to": "table", "distance_m": 11.43, "steps": 15},
    {"from": "table", "to": "stair1", "distance_m": 6.1, "steps": 8},
    {"from": "table", "to": "lift", "distance_m": 8.38, "steps": 11},
    {"from": "stair1", "to": "lift", "distance_m": 6.86, "steps": 9},
    {"from": "stair1", "to": "office", "distance_m": 6.86, "steps": 9},
    
    {"from": "office", "to": "cabin1", "distance_m": 2.0, "steps": 3},
    {"from": "cabin1", "to": "cabin2", "distance_m": 2.0, "steps": 3},
    {"from": "cabin2", "to": "cabin3", "distance_m": 2.0, "steps": 3},
    
    {"from": "office", "to": "class1", "distance_m": 5.33, "steps": 7},
    {"from": "class1", "to": "meeting", "distance_m": 3.81, "steps": 5},
    {"from": "meeting", "to": "class2_1", "distance_m": 6.86, "steps": 9},
    {"from": "class2_1", "to": "class2_2", "distance_m": 18.29, "steps": 24},
    {"from": "class2_2", "to": "class3", "distance_m": 3.81, "steps": 5},
    {"from": "class3", "to": "sem_turn", "distance_m": 4.0, "steps": 5},
    
    {"from": "sem_turn", "to": "seminar", "distance_m": 10.0, "steps": 14}, # Split the 20.57 distance
    {"from": "sem_turn", "to": "wash_turn", "distance_m": 5.0, "steps": 7},
    {"from": "wash_turn", "to": "water_room", "distance_m": 3.0, "steps": 4},
    {"from": "water_room", "to": "stair2", "distance_m": 2.5, "steps": 3},
    {"from": "stair2", "to": "window", "distance_m": 4.0, "steps": 5},
    
    {"from": "wash_turn", "to": "boys", "distance_m": 13.72, "steps": 18}, # washroom gents
    {"from": "water_room", "to": "girls", "distance_m": 3.05, "steps": 4}  # washroom ladies
]

out = {
    "floor_name": "Ground Floor",
    "floor_id": "GF",
    "nodes": nodes,
    "edges": edges
}

with open("department_pathfinder/data/ground_floor.json", "w") as f:
    json.dump(out, f, indent=2)

print("Created perfect visual graph in ground_floor.json")
