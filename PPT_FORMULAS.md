# Smart Path Suggestor - Formulas for PPT

---

## 📏 Distance Calculation from MiDaS

### Formula
```
Distance (meters) = SCALE / (MiDaS_Value + ε)
```

### Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **SCALE** | 775 | Calibration constant |
| **MiDaS_Value** | 0-255 | Depth value from MiDaS model |
| **ε (epsilon)** | 0.000001 | Prevents division by zero |

### Example

| MiDaS Value | Distance (meters) |
|-------------|-------------------|
| 310 | 2.5 m |
| 155 | 5.0 m |
| 103 | 7.5 m |

---

## ⚠️ Risk Estimation

### Formula
```
Risk = W × Proximity × M
```

### Parameters

| Parameter | Formula | Range | Meaning |
|-----------|---------|-------|---------|
| **W** (Weight) | Object priority | 2.0 - 10.0 | Higher for dangerous objects (vehicle=10, person=7) |
| **Proximity** | min(1.0, 2.0/(d+0.1)) | 0.0 - 1.0 | Closer objects = higher value |
| **M** (Multiplier) | Vertical position | 0.7 - 2.0 | Bottom zone=2.0, Middle=1.2, Top=0.7 |

### Risk Example

**Object**: Pothole at 2.5 meters, bottom of frame

| Step | Calculation | Value |
|------|-------------|-------|
| Weight (W) | Pothole priority | 9.0 |
| Proximity | min(1.0, 2.0/(2.5+0.1)) | 0.77 |
| Multiplier (M) | Bottom zone | 2.0 |
| **Final Risk** | 9.0 × 0.77 × 2.0 | **13.9** |

---

## 📊 Object Risk Weights

| Object | Weight | Priority |
|--------|--------|----------|
| Vehicles (car, truck, bus) | 10.0 | Extreme |
| Pothole, stairs down | 9.0 | Very High |
| Person, dog | 7.0 | High |
| Bicycle | 6.0 | Medium |
| Wall, pole | 4.0-5.0 | Low |

---

## 🚨 Distance Thresholds

| Distance | Priority | Action |
|----------|----------|--------|
| ≤ 3.0 m | CRITICAL | Stop immediately |
| ≤ 5.0 m | DANGER | Slow down |
| ≤ 7.0 m | WARN | Early warning |
| > 7.0 m | CLEAR | Continue walking |
