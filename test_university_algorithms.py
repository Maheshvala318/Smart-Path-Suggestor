import sys
import os

# Add the pathfinding_algorithms directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'pathfinding_algorithms')))

from dijkstra_algorithm import get_dijkstra_path
from astar_algorithm import get_astar_path

def test_algorithms():
    test_cases = [
        ("ADMIN BUILDING (TOWER)", "LIBRARY"),
        ("B K SCHOOL OF BUSINESS", "DEPARTMENT OF COMPUTER SCIENCE"),
        ("DEPARTMENT OF PHYSICS", "GUSEC"),
        ("TOWER CIRCLE", "GATE NO 1")
    ]
    
    for source, dest in test_cases:
        print(f"\nTesting path from: {source} TO: {dest}")
        
        # Test Dijkstra
        d_result, d_error = get_dijkstra_path(source, dest)
        if d_error:
            print(f"Dijkstra Error: {d_error}")
        else:
            print(f"Dijkstra: {d_result['distance']}m, Path length: {len(d_result['path'])}")
            print(f"Path: {' -> '.join(d_result['path'])}")
            
        # Test A*
        a_result, a_error = get_astar_path(source, dest)
        if a_error:
            print(f"A* Error: {a_error}")
        else:
            print(f"A*: {a_result['distance']}m, Path length: {len(a_result['path'])}")
            print(f"Path: {' -> '.join(a_result['path'])}")
            
        if not d_error and not a_error:
            if d_result['distance'] == a_result['distance']:
                print("SUCCESS: Both algorithms found the same shortest distance.")
            else:
                print("WARNING: Algorithms found different distances!")

if __name__ == "__main__":
    test_algorithms()
