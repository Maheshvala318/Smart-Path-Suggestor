# Pathfinding Algorithms - Separate Project

This folder contains standalone implementations of graph-based pathfinding algorithms for the Smart Path Suggestor project. These notebooks are currently isolated and will be integrated into the main project later.

---

## 📋 Project Overview

### Purpose
These implementations explore different shortest-path algorithms applied to a real-world campus navigation scenario (Gujarat University). The goal is to find optimal routes between departments, buildings, and gates on campus.

### Notebooks Analyzed

#### 1. **presentation.ipynb**
**Algorithms**: Dijkstra's Algorithm & A* Algorithm

Contains two complete implementations with graph-based pathfinding:

**Dijkstra Algorithm:**
- Uses priority queue (greedy approach)
- Finds shortest path from source to destination
- Implementation: Adjacency matrix with 76 campus nodes
- Time Complexity: O((V + E) log V)
- Visualizes path using NetworkX and Matplotlib

**A* Algorithm:**
- Informed search using Euclidean distance heuristic
- Formula: f(n) = g(n) + h(n)
  - g(n) = actual cost from start
  - h(n) = heuristic estimate to goal
- More efficient than Dijkstra for many scenarios
- Includes execution time tracking (nanosecond precision)

**Key Features:**
- 76 vertices representing campus locations (departments, gates, buildings, intersections)
- Weighted edges representing distances in meters
- Scaling visualization for better readability
- Path highlighting with yellow nodes and green edges
- Distance displayed in both meters and kilometers

---

#### 2. **Final1.ipynb**
**Algorithms**: Dijkstra, A*, DFS, BFS, Bellman-Ford + GUI

Complete Tkinter GUI application for interactive path finding:

**Algorithms Implemented:**
1. **Dijkstra** - Uses NetworkX library (weighted graph shortest path)
2. **A*** - Custom implementation with `haversine` heuristic
3. **DFS (Depth-First Search)** - Recursive exploration
4. **BFS (Breadth-First Search)** - Queue-based level exploration
5. **Bellman-Ford** - Works with negative weights (edge case handling)

**GUI Features:**
- Interactive map widget (TkinterMapView)
- Dropdown menus for source/destination selection
- Algorithm selector
- Live visualization of paths on map
- Distance calculation display
- Real GPS coordinates (latitude/longitude) for all 47 campus locations (subset of full 76-node graph)

**Map Features:**
- Centered at Gujarat University (23.0375°, 72.5465°)
- Zoom level 17 for detailed campus view
- Markers for each location
- Path drawn as lines connecting nodes
- Distance in meters displayed

---

## 🔄 Campus Graph Structure

### Node Data
- **Total Nodes in Dijkstra/A***: 76 (full campus map)
- **Active Nodes in Final1**: 47 (major locations with GPS)
- **Total Edges**: 100+ connections

### Node Categories

**Academic Departments:**
- Computer Science, Physics, Chemistry, Zoology, Botany
- Microbiology, Biochemistry, Mathematics, Psychology, Animation
- Languages, International Studies & Diaspora

**Administrative:**
- Admin Building (Tower), Examination Centre, Information Centre
- Police Station, Multiple Gates (Entry/Exit points)

**Facilities:**
- Library, Canteen, GUSEC, School of Design
- Physical Research Laboratory (PRL), Atal Kalam

**Infrastructure:**
- 51 numbered intersections/waypoints
- 4 main gates: Gate No 1, Netaji, Mahatma Gandhi, Dr. Ambedkar

---

## 📊 Algorithms Comparison

| Algorithm | Time Complexity | Space | Handles Negative Weights | Heuristic | Best Use Case |
|-----------|-----------------|-------|--------------------------|-----------|---------------|
| **Dijkstra** | O((V+E) log V) | O(V) | ❌ No | ❌ No | Single source shortest path |
| **A*** | O(E) avg-case | O(V) | ❌ No | ✅ Yes | Faster pathfinding with heuristic |
| **DFS** | O(V + E) | O(V) | ✅ Yes | ❌ No | Path existence, deep exploration |
| **BFS** | O(V + E) | O(V) | ✅ Yes | ❌ No | Shortest unweighted path |
| **Bellman-Ford** | O(VE) | O(V) | ✅ Yes | ❌ No | Negative weights, robustness |

---

## 🎯 Key Implementation Details

### Distance Calculation

**Method: Haversine Formula** (for GPS coordinates in Final1)
```
R = 6,371,000 meters (Earth's radius)
distance = 2R * arcsin(√(sin²(Δlat/2) + cos(lat₁) * cos(lat₂) * sin²(Δlon/2)))
```

### Graph Representation

**Presentation.ipynb:**
- Adjacency Matrix: 76×76 matrix with edge weights
- Direct distance values in meters
- Bidirectional edges (undirected graph)

**Final1.ipynb:**
- NetworkX Graph object
- Node positions as (latitude, longitude) tuples
- Edge weights calculated via haversine distance

---

## 🚀 Requirements

### Dependencies

```
networkx           # Graph data structures and algorithms
matplotlib         # Visualization of paths
tkinter            # GUI framework (comes with Python)
tkintertmapview    # Interactive map widget
heapq              # Priority queue for Dijkstra/A*
math               # Trigonometric functions (haversine)
```

### Installation

```bash
pip install networkx matplotlib tkintertmapview
```

---

## ▶️ How to Run (Currently Standalone)

### Run Dijkstra Algorithm (Presentation.ipynb)
```bash
jupyter notebook presentation.ipynb
# Select first cell to run Dijkstra implementation
# Input: Source and destination node names
# Output: Shortest path and distance, visualization
```

### Run A* Algorithm (Presentation.ipynb)
```bash
jupyter notebook presentation.ipynb
# Select second cell to run A* implementation
# Input: Source and destination node names
# Output: Shortest path, distance, execution time
```

### Run GUI Application (Final1.ipynb)
```bash
jupyter notebook Final1.ipynb
# Or extract to Python:
python gui_pathfinder.py
# Select source and destination from dropdowns
# Choose algorithm from dropdown
# Click "Find Path"
# View interactive map and results
```

---

## 📝 Campus Node Examples

### Major Departments
```
DEPARTMENT OF COMPUTER SCIENCE (Node 7)
DEPARTMENT OF PHYSICS (Node 9)
DEPARTMENT OF CHEMISTRY (Node 15)
DEPARTMENT OF ZOOLOGY (Node 10)
```

### Entry/Exit Points
```
GATE NO 1
NETAJI SUBHASH CHANDRA BOSE GATE
MAHATMA GANDHI GATE
DR BABA SAHEB AMBEDKAR GATE
```

### Waypoints
```
Numbered nodes: 2, 3, 4, 5... up to 51
These represent intersections and pathways
```

---

## 🔗 Integration Plan (Phase 2)

When integrating with main Smart Path Suggestor project:

1. **Extract Algorithm Implementations**
   - Create separate Python modules for each algorithm
   - Remove Jupyter-specific code

2. **API Integration**
   - Add endpoints to Flask/FastAPI server
   - Accept source/destination query parameters
   - Return JSON with path and distance

3. **Database Integration**
   - Store graph structure in database
   - Cache computed paths for frequently used routes
   - Update node positions dynamically

4. **Voice/Mobile Integration**
   - Connect to voice recognition system
   - Support voice input for source/destination
   - Integrate with mobile app navigation

5. **Real-time Features**
   - Add accessibility settings (prefer elevators, ramps)
   - Traffic/crowd awareness
   - Alternative route suggestions
   - ETA calculations

---

## 📌 Current Status

- ✅ Dijkstra implementation complete
- ✅ A* implementation complete
- ✅ GUI prototype complete
- ✅ 5 algorithms compared
- ⏳ Standalone testing phase
- ⏳ Integration with main project (pending)

---

## 🔍 Testing Notes

**Dijkstra & A* Work Best With:**
- Major destinations (departments, gates)
- Multi-hop paths (requires traversal through multiple nodes)

**Example Queries:**
- "From ADMIN BUILDING to LIBRARY"
- "From GATE NO 1 to DEPARTMENT OF COMPUTER SCIENCE"

**Known Limitations:**
- Some nodes may not be directly connected (requires waypoint traversal)
- Distance accuracy depends on GPS coordinate precision
- GUI zoom level may need adjustment for different screen sizes

---

## 📂 File Structure
```
pathfinding_algorithms/
├── README.md                    # This file
├── dijkstra_implementation.py   # (To be extracted)
├── astar_implementation.py      # (To be extracted)
├── gui_pathfinder.py            # (To be extracted from Final1)
├── data/
│   ├── campus_nodes.json        # Node coordinates
│   └── campus_edges.json        # Edge connections
└── requirements.txt             # Dependencies
```

---

## ✅ Next Steps

1. Extract Python code from notebooks into standalone files
2. Create requirements.txt with dependencies
3. Add command-line interface for quick testing
4. Add unit tests for algorithms
5. Validate paths on real campus routes
6. Prepare for main project integration

---

**Last Updated**: April 25, 2026
**Status**: Isolated Phase (Testing & Analysis)
**Integration Target**: Smart Path Suggestor Main System (Early Beta)
