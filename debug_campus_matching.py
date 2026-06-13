
import sys
import os

# Add relevant paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'pathfinding_algorithms')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'department_pathfinder')))

from astar_algorithm import initialize_campus_graph
from campus_map_data import CAMPUS_NODES

def debug_matching():
    g = initialize_campus_graph()
    labels = [label for label in g.vertex_data if label]
    
    print(f"Total graph nodes: {len(labels)}")
    print(f"Total campus nodes in data file: {len(CAMPUS_NODES)}")
    
    mismatches = []
    for label in labels:
        if label not in CAMPUS_NODES:
            # Try case-insensitive
            found = False
            for c_name in CAMPUS_NODES:
                if c_name.upper() == label.upper():
                    found = True
                    break
            if not found:
                mismatches.append(label)
                
    if mismatches:
        print(f"\nFound {len(mismatches)} mismatches:")
        for m in mismatches[:10]:
            print(f"  - '{m}'")
    else:
        print("\nAll graph labels match campus data keys!")

if __name__ == "__main__":
    debug_matching()
