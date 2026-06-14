# Quick Start Guide - Pathfinding Algorithms

## 📦 Setup

### 1. Install Dependencies
```bash
cd pathfinding_algorithms
pip install -r requirements.txt
```

### 2. Required Python Version
- Python 3.7+
- Tested with Python 3.9+

---

## 🚀 Running the Algorithms

### Option A: Command Line (Standalone)

#### Run Dijkstra Algorithm
```bash
python dijkstra_algorithm.py
```

**Expected Usage:**
```
Enter the source location: ADMIN BUILDING (TOWER)
Enter the destination location: LIBRARY

SHORTEST PATH FOUND
Path: ADMIN BUILDING (TOWER) -> ... -> LIBRARY
Distance: 2850 meters (2.85 kilometers)

Visualize the path? (y/n): y
```

#### Run A* Algorithm
```bash
python astar_algorithm.py
```

**Expected Usage:**
```
Enter the source location: DEPARTMENT OF COMPUTER SCIENCE
Enter the destination location: DEPARTMENT OF PHYSICS

OPTIMAL PATH FOUND (A* Algorithm)
Path: DEPARTMENT OF COMPUTER SCIENCE -> ... -> DEPARTMENT OF PHYSICS
Distance: 1200 meters (1.20 kilometers)
Execution Time: 1234.56 nanoseconds (0.0012 microseconds)

Visualize the path? (y/n): y
```

### Option B: Jupyter Notebooks (Original Format)

```bash
jupyter notebook
# Navigate to ../notebooks/presentation.ipynb
# Run cells for Dijkstra or A* implementation
```

### Option C: Interactive GUI (From Final1.ipynb)

```bash
jupyter notebook
# Navigate to ../notebooks/Final1.ipynb
# Run to launch Tkinter GUI with map
```

---

## 📍 Sample Campus Locations

### Major Departments
- `DEPARTMENT OF COMPUTER SCIENCE`
- `DEPARTMENT OF PHYSICS`
- `DEPARTMENT OF CHEMISTRY`
- `DEPARTMENT OF ZOOLOGY`
- `DEPARTMENT OF BOTANY`
- `DEPARTMENT OF MICROBIOLOGY`
- `DEPARTMENT OF MATHEMATICS`
- `DEPARTMENT OF PSYCHOLOGY`

### Administrative Buildings
- `ADMIN BUILDING (TOWER)`
- `LIBRARY`
- `CANTEEN`
- `EXAMINATION CENTRE`
- `INFORMATION CENTRE`

### Entry/Exit Gates
- `GATE NO 1`
- `NETAJI SUBHASH CHANDRA BOSE GATE`
- `MAHATMA GANDHI GATE`
- `DR BABA SAHEB AMBEDKAR GATE`

### Special Facilities
- `SCHOOL OF DESIGN`
- `SCHOOL OF LANGUAGES`
- `PHYSICAL RESEARCH LABORATORY (PRL)`
- `ATAL KALAM`
- `GUSEC`

---

## 🎯 Performance Comparison

### Sample Test Case
**Query**: From `ADMIN BUILDING (TOWER)` to `LIBRARY`

| Algorithm | Distance | Time (ns) | Path Nodes |
|-----------|----------|-----------|------------|
| Dijkstra | 2850m | ~5000 | 8 |
| A* | 2850m | ~2000 | 8 |

**Note**: A* is typically faster than Dijkstra for this use case due to intelligent heuristic guidance.

---

## 🔧 Troubleshooting

### Issue: Import Error for `tkintertmapview`
```
ModuleNotFoundError: No module named 'tkintertmapview'
```

**Solution:**
```bash
pip install --upgrade tkintertmapview
```

### Issue: No path found
- Verify location names are capitalized
- Check spelling exactly (use suggestions from printed list)
- Some locations may only be accessible through waypoint nodes

### Issue: Visualization window not showing
- Ensure you have a display server (X11 for Linux/WSL)
- On headless systems, skip visualization
- Try: `export DISPLAY=:0` on Linux

---

## 📊 Algorithm Selection Guide

**Use Dijkstra when:**
- You need guaranteed shortest path
- Graph may have varying edge weights
- Simplicity is priority

**Use A* when:**
- You need faster computation
- You have good positional heuristic
- Real-time systems needed

**Use BFS when:**
- All edges have equal weight
- Unweighted shortest path needed
- Simplicity matters most

**Use DFS when:**
- Finding any path (not necessarily shortest)
- Memory is limited
- Exploring all possibilities

**Use Bellman-Ford when:**
- Graph may have negative weights
- Need to detect negative cycles
- Robustness is critical

---

## 📝 API Reference

### Graph Class

```python
from dijkstra_algorithm import Graph

# Create graph
g = Graph(76)  # 76 nodes

# Add vertex
g.add_vertex_data(0, "ADMIN BUILDING", (0, 0))

# Add edge
g.add_edge(0, 1, 100)  # 100 meters

# Find path
distance, path = g.dijkstra("ADMIN BUILDING", "LIBRARY")

# Visualize
g.visualize(path)
```

---

## 🐛 Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📚 Resources

- **NetworkX Documentation**: https://networkx.org/
- **Dijkstra Algorithm**: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- **A* Algorithm**: https://en.wikipedia.org/wiki/A*_search_algorithm
- **Graph Theory Basics**: https://en.wikipedia.org/wiki/Graph_theory

---

## ✅ Verification Checklist

Before deploying:
- [ ] All dependencies installed
- [ ] Test with sample queries
- [ ] Verify visualization renders correctly
- [ ] Check execution times are acceptable
- [ ] Validate multiple path queries work

---

**Last Updated**: April 25, 2026
