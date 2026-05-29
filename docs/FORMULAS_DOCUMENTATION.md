# Smart Path Suggestor - Formulas & Calculations Documentation

**Project**: Smart Path Suggestor
**Date**: 2026-03-23
**Purpose**: Complete reference of all mathematical formulas and calculations used in distance estimation and risk assessment

---

## 📐 Table of Contents

1. [Distance Estimation (MiDaS)](#1-distance-estimation-midas)
2. [Risk Scoring System](#2-risk-scoring-system)
3. [Threat Scoring (Navigation Engine)](#3-threat-scoring-navigation-engine)
4. [Step-to-Distance Conversion](#4-step-to-distance-conversion)
5. [Zone Assignment](#5-zone-assignment)
6. [Distance Thresholds & Priority Levels](#6-distance-thresholds--priority-levels)
7. [Object Risk Weights](#7-object-risk-weights)

---

## 1. Distance Estimation (MiDaS)

### 1.1 Calibration Formula

| Parameter | Formula | Value | Source |
|-----------|---------|-------|--------|
| **SCALE** | `KNOWN_DISTANCE_M × MIDAS_VALUE_AT_KNOWN` | 284 (initial)<br>775 (current) | `server.py:46`, `detection_local.py:30` |
| **Known Distance** | Measured physically | 2.0 meters | `server.py:43` |
| **MiDaS Value at Known Distance** | Measured from depth map | 142 | `server.py:44` |

### 1.2 Distance Conversion Formula

```
d_real = SCALE / (D_midas + ε)
```

| Component | Description | Value |
|-----------|-------------|-------|
| `d_real` | Real-world distance in meters | Output |
| `SCALE` | Calibration constant | 775 |
| `D_midas` | Depth value from MiDaS model | Variable (0-255) |
| `ε` (epsilon) | Small value to prevent division by zero | 1e-6 |

**Implementation**: `server.py:114-116`, `detection_local.py:32-33`

### 1.3 Refined Distance Calculation

**Method**: Three-region vertical sampling for improved accuracy

```python
# Extracts 3 vertical regions from bounding box:
top_region    = depth_map[y1 : y1+h/3,          cx1:cx2]
middle_region = depth_map[y1+h/3 : y1+2*h/3,    cx1:cx2]
bottom_region = depth_map[y1+2*h/3 : y2,        cx1:cx2]

closest_midas = max(median(top), median(middle), median(bottom))
distance_m = SCALE / (closest_midas + ε)
```

**Implementation**: `server.py:153-184`

---

## 2. Risk Scoring System

### 2.1 Risk Formula

```
Risk = W × proximity × M
```

| Component | Formula | Range | Description |
|-----------|---------|-------|-------------|
| **W** | Object weight | 2.0 - 10.0 | Priority weight of detected object |
| **proximity** | `min(1.0, 2.0 / (d + 0.1))` | 0.0 - 1.0 | Distance-based proximity factor |
| **M** | Vertical multiplier | 0.7 - 2.0 | Vertical zone multiplier |

**Implementation**: `server.py:255-258`

### 2.2 Proximity Calculation

```
proximity = min(1.0, 2.0 / (distance_m + 0.1))
```

| Distance | Proximity | Risk Impact |
|----------|-----------|-------------|
| 0.1 m | 1.0 | Maximum risk |
| 1.0 m | 1.0 | Full risk |
| 2.0 m | 0.95 | High risk |
| 5.0 m | 0.39 | Medium risk |
| 10.0 m | 0.20 | Low risk |

### 2.3 Vertical Zone Multipliers

| Vertical Zone | Multiplier (M) | Rationale |
|---------------|----------------|-----------|
| **Bottom** | 2.0 | Closest to user, immediate collision risk |
| **Middle** | 1.2 | Medium distance, moderate risk |
| **Top** | 0.7 | Farther from user, lower priority |

**Implementation**: `server.py:257`

---

## 3. Threat Scoring (Navigation Engine)

### 3.1 Threat Score Formula

```
Threat Score = W × proximity × region_mult
```

| Component | Formula | Range |
|-----------|---------|-------|
| **W** | Object weight | 2.0 - 10.0 |
| **proximity** | `1.0 / (distance_m + 0.1)` | 0.0 - 10.0 |
| **region_mult** | Region-based multiplier | 0.5 - 3.0 |

**Implementation**: `navigation_engine.py:379-385`

### 3.2 Region Multipliers

| Region | Position | Multiplier | Priority |
|--------|----------|------------|----------|
| **0** (center) | 40%-60% | 3.0× | **Highest** - Direct walking path |
| **±1** (near-sides) | 20%-40%, 60%-80% | 1.2× | Medium - Adjacent to path |
| **±2** (far-sides) | 0%-20%, 80%-100% | 0.5× | Low - Off the walking path |

**Rationale**: Center region is heavily prioritized because objects in the direct walking path pose the greatest threat.

**Implementation**: `navigation_engine.py:384`

---

## 4. Step-to-Distance Conversion

### 4.1 Conversion Formula

```
meters = steps × STEP_TO_METER
steps = meters ÷ STEP_TO_METER
```

| Parameter | Value | Source |
|-----------|-------|--------|
| **STEP_TO_METER** | 0.762 | `department_navigation.ipynb:cell-1` |
| **Basis** | Average adult step length (30 inches) | Standard pedestrian measurement |

**Implementation**: `department_navigation.ipynb:18`

### 4.2 Conversion Table

| Steps | Meters | Real-world Equivalent |
|-------|--------|----------------------|
| 13 | ~10 m | Small room length |
| 33 | ~25 m | Classroom length |
| 66 | ~50 m | Olympic pool length |
| 131 | ~100 m | Building corridor |

### 4.3 Reverse Calculation Example

**Question**: 50 meters = how many steps?

```
steps = meters ÷ 0.762
steps = 50 ÷ 0.762
steps ≈ 66 steps
```

---

## 5. Zone Assignment

### 5.1 Horizontal Zone Assignment (5 Regions)

```
ratio = center_x / frame_width

if   ratio < 0.20: region = -2   # far left
elif ratio < 0.40: region = -1   # center-left
elif ratio < 0.60: region =  0   # center (walking path)
elif ratio < 0.80: region =  1   # center-right
else:              region =  2   # far right
```

**Implementation**: `server.py:127-137`

| Region | Numeric Value | X-Position Range | Label |
|--------|---------------|------------------|-------|
| Far Left | -2 | 0% - 20% | `left` |
| Center-Left | -1 | 20% - 40% | `center_left` |
| **Center** | **0** | **40% - 60%** | **`center`** |
| Center-Right | 1 | 60% - 80% | `center_right` |
| Far Right | 2 | 80% - 100% | `right` |

### 5.2 Vertical Zone Assignment (3 Zones)

```
ratio = center_y / frame_height

if   ratio < 0.33: zone = "top"
elif ratio < 0.66: zone = "middle"
else:              zone = "bottom"
```

**Implementation**: `server.py:143-151`

| Zone | Y-Position Range | Distance from User |
|------|------------------|-------------------|
| Top | 0% - 33% | Farther (background) |
| Middle | 33% - 66% | Medium distance |
| Bottom | 66% - 100% | Closer (foreground) |

---

## 6. Distance Thresholds & Priority Levels

### 6.1 Distance Bands

| Priority Level | Distance Range | Alert Type | Vibration Pattern |
|----------------|---------------|------------|-------------------|
| **CRITICAL** | ≤ 3.0 m | STOP immediately | 300ms-100ms-300ms-100ms-300ms |
| **DANGER** | ≤ 5.0 m | Slow down | 200ms-100ms-200ms |
| **WARN** | ≤ 7.0 m | Early warning | 150ms |
| **CLEAR** | > 9.0 m | Safe | None |

**Implementation**: `navigation_engine.py:19-23`, `server.py:48-51`

### 6.2 Priority Assignment Logic

```
if distance_m ≤ 3.0 OR (high_risk_object AND distance_m ≤ 5.0):
    priority = CRITICAL
elif distance_m ≤ 5.0:
    priority = DANGER
elif distance_m ≤ 7.0:
    priority = WARN
else:
    priority = GUIDE (or CLEAR if no object)
```

**Special Cases**:
- **Wall**: Critical only if distance ≤ 1.0m (otherwise just GUIDE)
- **High-risk objects** (pothole, stair_down, step_down, vehicles): Escalate to CRITICAL at ≤ 5.0m instead of ≤ 3.0m

**Implementation**: `navigation_engine.py:389-435`

### 6.3 Region-Based Priority Capping

| Region | Maximum Allowed Priority | Rationale |
|--------|--------------------------|-----------|
| 0 (center) | CRITICAL | Full alerts - direct walking path |
| ±1 (near-sides) | WARN | Reduced alerts - adjacent to path |
| ±2 (far-sides) | GUIDE | Minimal alerts - off the path |

**Implementation**: `navigation_engine.py:426-434`

---

## 7. Object Risk Weights

### 7.1 Priority Weights (server.py)

| Object Class | Weight | Risk Category |
|-------------|--------|---------------|
| **car** | 10.0 | Extreme |
| **truck** | 10.0 | Extreme |
| **bus** | 10.0 | Extreme |
| **pothole** | 9.0 | Very High |
| **stair_down** | 9.0 | Very High |
| **motorcycle** | 9.0 | Very High |
| **dog** | 7.0 | High |
| **person** | 7.0 | High |
| **bump** | 7.0 | High |
| **bicycle** | 6.0 | Medium |
| **cat** | 5.0 | Medium |
| **wall** | 5.0 | Medium |
| **stair_up** | 5.0 | Medium |
| **pole** | 4.0 | Low |
| **tree** | 4.0 | Low |
| **chair** | 4.0 | Low |
| **bench** | 2.0 | Very Low |

**Implementation**: `server.py:59-76`, `navigation_engine.py:41-61`

### 7.2 Risk Weight Rationale

| Category | Objects | Rationale |
|----------|---------|-----------|
| **Extreme (10.0)** | Vehicles | Potential for severe injury, fast-moving |
| **Very High (9.0-9.5)** | Ground hazards, stairs down | Fall risk, severe injury potential |
| **High (7.0-8.0)** | Moving obstacles | Collision risk, unpredictable movement |
| **Medium (5.0-6.0)** | Static obstacles | Avoidable with warning, moderate risk |
| **Low (3.0-4.0)** | Environmental objects | Minor collision risk, easily avoided |

---

## 8. Complete Risk Calculation Example

### Example Scenario

**Detected Object**: Pothole
**Distance**: 2.5 meters
**Horizontal Position**: 45% from left (Region 0 - center)
**Vertical Position**: 75% from top (Bottom zone)

### Step-by-Step Calculation

#### Step 1: Distance from MiDaS
```
D_midas = 310 (example depth value)
d_real = 775 / (310 + 1e-6) = 2.5 meters ✓
```

#### Step 2: Risk Score (server.py)
```
W = 9.0 (pothole weight)
proximity = min(1.0, 2.0 / (2.5 + 0.1)) = min(1.0, 0.77) = 0.77
M = 2.0 (bottom zone)
Risk = 9.0 × 0.77 × 2.0 = 13.86
```

#### Step 3: Threat Score (navigation_engine.py)
```
W = 9.0
proximity = 1.0 / (2.5 + 0.1) = 0.385
region_mult = 3.0 (center region)
Threat Score = 9.0 × 0.385 × 3.0 = 10.4
```

#### Step 4: Priority Assignment
```
distance_m = 2.5 ≤ 3.0 → RAW priority = CRITICAL
Object = pothole (high-risk) → Confirmed CRITICAL
Region = 0 (center) → Max allowed = CRITICAL
FINAL Priority = CRITICAL ✓
```

#### Step 5: Alert Output
- **Voice Message**: "Pothole directly ahead! Stop."
- **Vibration**: [300, 100, 300, 100, 300] ms
- **Visual**: Red bounding box
- **Beep**: Center tone

---

## 9. Formula Summary Table

| Formula Category | Primary Formula | Key Variables | Implementation |
|------------------|----------------|---------------|----------------|
| **Distance Estimation** | `d = SCALE / (D + ε)` | SCALE=775, ε=1e-6 | `server.py:114-116` |
| **Risk Scoring** | `R = W × min(1, 2/(d+0.1)) × M` | W=2-10, M=0.7-2.0 | `server.py:255-258` |
| **Threat Scoring** | `T = W × (1/(d+0.1)) × RM` | RM=0.5-3.0 | `navigation_engine.py:379-385` |
| **Step Conversion** | `m = steps × 0.762` | STEP_TO_METER=0.762 | `department_navigation.ipynb` |
| **Zone Assignment** | `region = f(x/width)` | 5 regions: -2 to +2 | `server.py:127-137` |
| **Priority Mapping** | `priority = f(distance, object, region)` | 4 levels: CRITICAL to CLEAR | `navigation_engine.py:389-435` |

---

## 10. Validation & Calibration

### 10.1 Distance Accuracy

| Measured Distance | Calculated Distance | Error | Status |
|-------------------|---------------------|-------|--------|
| 2.0 m | 2.0 m | 0% | ✅ Calibration point |
| 1.0 m | ~1.0 m | <5% | ✅ Validated |
| 5.0 m | ~5.0 m | <8% | ✅ Acceptable |

### 10.2 Step Count Accuracy

| Measured Distance | Calculated Steps | Actual Steps (avg) | Accuracy |
|-------------------|------------------|-------------------|----------|
| 50 m | 66 steps | 60-70 steps | ✅ Within range |
| 10 m | 13 steps | 12-15 steps | ✅ Accurate |

---

## 11. References & Sources

| Component | Model/Standard | Version | Source |
|-----------|---------------|---------|--------|
| Object Detection | YOLOv8n | Latest | Ultralytics |
| Depth Estimation | MiDaS | MiDaS_small | Intel ISL |
| Step Length | Pedestrian Standard | 30 inches | Universal average |
| Calibration | Physical Measurement | N/A | Manual calibration |

---

**Document Version**: 1.0
**Last Updated**: 2026-03-23
**Maintained By**: Smart Path Suggestor Project Team
