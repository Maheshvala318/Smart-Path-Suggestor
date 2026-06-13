import csv
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from department_pathfinder.campus_map_data import CAMPUS_NODES, CAMPUS_EDGES

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

csv_path = 'campus_edges_with_distance.csv'
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Source', 'Source_Lat', 'Source_Lon', 'Destination', 'Dest_Lat', 'Dest_Lon', 'Distance_Meters'])
    for edge in CAMPUS_EDGES:
        node1, node2 = edge
        if node1 in CAMPUS_NODES and node2 in CAMPUS_NODES:
            lat1, lon1 = CAMPUS_NODES[node1]
            lat2, lon2 = CAMPUS_NODES[node2]
            dist = haversine(CAMPUS_NODES[node1], CAMPUS_NODES[node2])
            writer.writerow([node1, lat1, lon1, node2, lat2, lon2, round(dist, 2)])
        else:
            print(f"Warning: Missing coordinates for edge {edge}")

print(f"CSV successfully generated at {os.path.abspath(csv_path)}")
