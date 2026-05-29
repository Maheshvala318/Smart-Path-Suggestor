import cv2
import torch
import numpy as np
import time
from ultralytics import YOLO

from src.core.config import SCALE, CONFIDENCE_THRESHOLD, PRIORITY_WEIGHTS, DIST_DANGER
from src.vision_safety.safety_engine import NavigationEngine

print("=" * 50)
print("  Smart Path Suggestor — Loading Models...")
print("=" * 50)

print("[1/2] Loading YOLO Models...")
yolo_models = {
    "yolov8n": YOLO("models/yolov8n.pt"),
    "best": YOLO("models/best.pt")
}
print(f"      ✅ YOLO models loaded: {list(yolo_models.keys())}")

print("[2/2] Loading MiDaS...")
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", trust_repo=True)
midas.eval()
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
midas_transform  = midas_transforms.small_transform
device = torch.device("cpu")
midas.to(device)
print("      ✅ MiDaS loaded")

nav_engine = NavigationEngine()
print("      ✅ Navigation engine loaded")
print("=" * 50)

def midas_to_meters(depth_value):
    return SCALE / (float(depth_value) + 1e-6)

def get_zone(center_x, frame_width):
    ratio = center_x / frame_width
    if   ratio < 0.20: return -2
    elif ratio < 0.40: return -1
    elif ratio < 0.60: return  0
    elif ratio < 0.80: return  1
    else:              return  2

def region_to_label(region):
    return {-2: "left", -1: "center_left", 0: "center", 1: "center_right", 2: "right"}.get(region, "center")

def get_vertical_zone(center_y, frame_height):
    ratio = center_y / frame_height
    if ratio < 0.33:  return "top"
    elif ratio < 0.66: return "middle"
    else:              return "bottom"

def get_refined_distance(depth_map, x1, y1, x2, y2):
    bh = y2 - y1
    bw = x2 - x1
    cx1 = x1 + bw // 4
    cx2 = x2 - bw // 4

    h, w = depth_map.shape
    cx1 = max(0, min(w-1, cx1))
    cx2 = max(0, min(w-1, cx2))
    y1 = max(0, min(h-1, y1))
    y2 = max(0, min(h-1, y2))

    if cx1 >= cx2: cx2 = cx1 + 1

    regions = {
        'top':    depth_map[y1 : y1+bh//3,   cx1:cx2],
        'middle': depth_map[y1+bh//3 : y1+2*bh//3, cx1:cx2],
        'bottom': depth_map[y1+2*bh//3 : y2,       cx1:cx2],
    }

    medians = {k: float(np.median(v)) for k, v in regions.items() if v.size > 0}
    if not medians: return 10.0

    closest_midas = max(medians.values())
    return midas_to_meters(closest_midas)

def run_detection(frame, model_key="yolov8n"):
    yolo_model = yolo_models.get(model_key, yolo_models["yolov8n"])
    start_time = time.time()
    h, w       = frame.shape[:2]
    img_rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # YOLO
    yolo_results = yolo_model(frame, imgsz=480, verbose=False)
    boxes        = yolo_results[0].boxes

    # MiDaS
    input_batch = midas_transform(img_rgb).to(device)
    with torch.no_grad():
        prediction = midas(input_batch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img_rgb.shape[:2],
            mode="bilinear",
            align_corners=False,
        ).squeeze()
    depth_map = prediction.cpu().numpy()

    zone_risks = {-2: 0.0, -1: 0.0, 0: 0.0, 1: 0.0, 2: 0.0}
    detections   = []
    danger_found = False

    for box in boxes:
        conf = float(box.conf[0])
        if conf < CONFIDENCE_THRESHOLD: continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label = yolo_model.names[int(box.cls[0])]

        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(w, x2); y2 = min(h, y2)

        distance_m = get_refined_distance(depth_map, x1, y1, x2, y2)
        distance_m = round(distance_m, 2)

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        region   = get_zone(center_x, w)
        zone     = region_to_label(region)
        v_zone   = get_vertical_zone(center_y, h)

        priority  = PRIORITY_WEIGHTS.get(label, 3.0)
        proximity = min(1.0, 2.0 / (distance_m + 0.1))
        v_mult    = {"bottom": 2.0, "middle": 1.2, "top": 0.7}[v_zone]
        risk      = priority * proximity * v_mult

        zone_risks[region] = max(zone_risks[region], risk)

        if 0 < distance_m < DIST_DANGER:
            danger_found = True

        detections.append({
            "label":        label,
            "confidence":   round(conf, 2),
            "distance_m":   distance_m,
            "region":       region,
            "zone":         zone,
            "vertical":     v_zone,
            "risk":         round(risk, 2),
            "bbox":         [x1, y1, x2, y2],
        })

    detections.sort(key=lambda d: d["distance_m"])
    nav_result = nav_engine.process(detections, zone_risks)
    latency_ms = round((time.time() - start_time) * 1000, 1)

    return {
        "detections":     detections,
        "zone_risks":     {str(k): round(v, 2) for k, v in zone_risks.items()},
        "danger":         danger_found,
        "latency_ms":     latency_ms,
        "frame_size":     [w, h],
        "voice_message":  nav_result["voice_message"],
        "priority":       nav_result["priority"],
        "should_speak":   nav_result["should_speak"],
        "alert_type":     nav_result["alert_type"],
        "alert_pattern":  nav_result["alert_pattern"],
        "alert_duration": nav_result["alert_duration"],
        "beep_side":      nav_result.get("beep_side", "center"),
        "safe_direction": nav_result["safe_direction"],
        "safe_zone":      nav_result["safe_zone"],
    }
