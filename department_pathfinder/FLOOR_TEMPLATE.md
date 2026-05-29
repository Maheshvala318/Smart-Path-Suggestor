# 🏫 Floor Data Template — How to Add a New Floor

Use this template to create JSON data files for additional floors in the Department Path Finder.

---

## Step 1: Create the Floor Image

Draw or photograph your floor layout showing:
- **Red circles** (🔴) = Points of interest (rooms, stairs, facilities, landmarks)
- **Black lines** = Corridors / walkable paths connecting points
- **Blue labels** = Names of each point
- **Large arrows** = Staircases / Lifts (these are **connection points** between floors)

---

## Step 2: Create a JSON File

Save as `department_pathfinder/data/<floor_name>.json` (e.g., `first_floor.json`).

### JSON Structure

```json
{
  "floor_name": "First Floor",
  "floor_id": "1F",
  "nodes": {
    "unique_node_id": {
      "label": "Human Readable Name",
      "x": 100,
      "y": 200,
      "type": "room"
    }
  },
  "edges": [
    {
      "from": "node_id_a",
      "to": "node_id_b",
      "distance_m": 5.0,
      "steps": 7
    }
  ]
}
```

### Node Types
| Type | Use For |
|------|---------|
| `entrance` | Main doors, entry points |
| `room` | Classrooms, cabins, labs, offices |
| `facility` | Washrooms, toilets, water rooms |
| `stairs` | Staircases, lifts (connection points between floors) |
| `corridor` | Corridor junctions, turns |
| `landmark` | Tables, windows, notable points |

### Position (x, y) Guidelines
- The SVG viewBox is `1350 x 700` pixels.
- `x=0` is the **left** edge, `x=1350` is the **right** edge.
- `y=0` is the **top** edge, `y=700` is the **bottom** edge.
- Place nodes roughly proportional to their real-world position in the floor plan.

---

## Step 3: Connect Floors (Stairs/Lifts)

To connect floors, add **cross-floor edges** in _either_ floor's JSON file:

```json
{
  "from": "staircase_1",
  "to": "1F::staircase_1",
  "distance_m": 4.0,
  "steps": 40,
  "cross_floor": true
}
```

> **Convention**: Use `FLOOR_ID::node_id` format when referencing a node on a different floor.
> Example: `"1F::staircase_1"` refers to `staircase_1` on the First Floor.

### Connection Points in Ground Floor
The ground floor has these stair/lift nodes that should be connected:
- `staircase_1` — Left side staircase
- `staircase_2` — Right side staircase
- `lift` — Central lift

---

## Step 4: Measure Distances

For each edge, you need:
- **`distance_m`** — Distance in meters (measure or estimate)
- **`steps`** — Number of walking steps (`1 step ≈ 0.76 meters`)

**Quick formula**: `steps ≈ distance_m / 0.76`

---

## Step 5: Verify

After adding a new floor JSON file, restart the app:

```bash
cd department_pathfinder
python app.py
```

The new floor will automatically appear as a tab in the map view. Test a cross-floor route to verify connectivity.

---

## Example: First Floor Template

```json
{
  "floor_name": "First Floor",
  "floor_id": "1F",
  "nodes": {
    "staircase_1":   {"label": "Staircase 1",    "x": 160, "y": 450, "type": "stairs"},
    "staircase_2":   {"label": "Staircase 2",    "x": 1050,"y": 380, "type": "stairs"},
    "lift":          {"label": "Lift",            "x": 430, "y": 450, "type": "stairs"},
    "lab_1":         {"label": "Lab 1",           "x": 300, "y": 200, "type": "room"},
    "lab_2":         {"label": "Lab 2",           "x": 500, "y": 200, "type": "room"},
    "corridor_main": {"label": "Main Corridor",   "x": 600, "y": 350, "type": "corridor"}
  },
  "edges": [
    {"from": "staircase_1", "to": "corridor_main", "distance_m": 10.0, "steps": 13},
    {"from": "corridor_main", "to": "lab_1",       "distance_m": 6.0,  "steps": 8},
    {"from": "corridor_main", "to": "lab_2",       "distance_m": 4.0,  "steps": 5},
    {"from": "corridor_main", "to": "lift",        "distance_m": 5.0,  "steps": 7},
    {"from": "corridor_main", "to": "staircase_2", "distance_m": 10.0, "steps": 13}
  ]
}
```

---

## Checklist for Each New Floor

- [ ] Draw/photograph the floor layout
- [ ] Identify all POIs (rooms, stairs, facilities)
- [ ] Assign unique `node_id` to each POI
- [ ] Measure distances between connected POIs
- [ ] Create the JSON file in `data/`
- [ ] Add cross-floor edges to connect stair/lift nodes
- [ ] Restart app and verify paths work
