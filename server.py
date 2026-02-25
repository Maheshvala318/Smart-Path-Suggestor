# ============================================================
#  server.py  —  Smart Path Suggestor API Server
#  Run this on your laptop connected to university WiFi.
#  Mobile device connects via: http://YOUR_LAPTOP_IP:5000
# ============================================================
#
#  Install requirements:
#     pip install flask ultralytics torch torchvision opencv-python numpy
#
#  Find your laptop IP:
#     Windows  → ipconfig       (look for IPv4 Address)
#     Mac/Linux→ ifconfig | grep "inet "
#
#  Start server:
#     python server.py
#
#  Test from browser:
#     http://YOUR_IP:5000/health
# ============================================================

import cv2
import torch
import numpy as np
import time
import base64
import json
from flask import Flask, request, jsonify, send_file
from ultralytics import YOLO
from navigation_engine import NavigationEngine

app = Flask(__name__)

# ─────────────────────────────────────────────
#  CONFIGURATION  (edit these as needed)
# ─────────────────────────────────────────────

# MiDaS calibration — same as your original code
KNOWN_DISTANCE_M      = 2.0
MIDAS_VALUE_AT_KNOWN  = 142
SCALE                 = KNOWN_DISTANCE_M * MIDAS_VALUE_AT_KNOWN

# Distance threshold for danger alert (meters)
DANGER_DISTANCE_M     = 1.5   # warn at 1.5m  (your original was 0.5m — too close)
CRITICAL_DISTANCE_M   = 0.8   # critical at 0.8m

# Minimum YOLO confidence to show a detection
CONFIDENCE_THRESHOLD  = 0.40

# Zone boundaries — now 5 zones (handled in get_zone())

# Object priority weights for risk scoring (same logic as plan)
PRIORITY_WEIGHTS = {
    "person":      7.0,
    "car":        10.0,
    "truck":      10.0,
    "bus":        10.0,
    "motorcycle":  9.0,
    "bicycle":     6.0,
    "dog":         7.0,
    "cat":         5.0,
    "chair":       4.0,
    "pothole":     9.0,
    "stair_down":  9.0,
    "stair_up":    5.0,
    "bump":        7.0,
    "pole":        4.0,
    "tree":        4.0,
}

# ─────────────────────────────────────────────
#  LOAD MODELS  (once at startup)
# ─────────────────────────────────────────────

print("=" * 50)
print("  Smart Path Suggestor — Loading models...")
print("=" * 50)

print("[1/2] Loading YOLO...")
yolo_model = YOLO("yolov8n.pt")   # swap to yolov8s.pt when you have fine-tuned model
print("      ✅ YOLO loaded")

print("[2/2] Loading MiDaS...")
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", trust_repo=True)
midas.eval()
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
midas_transform  = midas_transforms.small_transform
device = torch.device("cpu")
midas.to(device)
print("      ✅ MiDaS loaded")

print("[3/3] Loading Navigation Engine...")
nav_engine = NavigationEngine()
print("      ✅ Navigation engine loaded")

print("=" * 50)
print("  ✅ All models ready. Server starting...")
print("=" * 50)

# ─────────────────────────────────────────────
#  HELPER FUNCTIONS  (same logic as your code)
# ─────────────────────────────────────────────

def midas_to_meters(depth_value):
    """Convert MiDaS relative depth to approximate meters (your calibration)"""
    return SCALE / (float(depth_value) + 1e-6)


def decode_base64_image(b64_string):
    """Convert base64 string from phone → OpenCV frame"""
    img_bytes = base64.b64decode(b64_string)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame     = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame


def get_zone(center_x, frame_width):
    """Return 5-zone position based on object x position"""
    ratio = center_x / frame_width
    if   ratio < 0.20: return "left"
    elif ratio < 0.40: return "center_left"
    elif ratio < 0.60: return "center"
    elif ratio < 0.80: return "center_right"
    else:              return "right"


def get_vertical_zone(center_y, frame_height):
    """Return top / middle / bottom — bottom objects are closest to user"""
    ratio = center_y / frame_height
    if ratio < 0.33:
        return "top"
    elif ratio < 0.66:
        return "middle"
    else:
        return "bottom"


# generate_voice_message() removed — NavigationEngine handles this now


# ─────────────────────────────────────────────
#  CORE DETECTION FUNCTION
# ─────────────────────────────────────────────

def run_detection(frame):
    """
    Full pipeline: YOLO + MiDaS + risk scoring + voice message.
    Input:  OpenCV frame (BGR)
    Output: dict with detections + voice message + zone risks
    """
    start_time = time.time()
    h, w       = frame.shape[:2]
    img_rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ── YOLO detection ────────────────────────────────────────
    yolo_results = yolo_model(frame, imgsz=480, verbose=False)
    boxes        = yolo_results[0].boxes

    # ── MiDaS depth map ───────────────────────────────────────
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

    # ── Per-object analysis ───────────────────────────────────
    zone_risks = {
        "left":         0.0,
        "center_left":  0.0,
        "center":       0.0,
        "center_right": 0.0,
        "right":        0.0,
    }
    detections   = []
    danger_found = False

    for box in boxes:
        conf  = float(box.conf[0])
        if conf < CONFIDENCE_THRESHOLD:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label           = yolo_model.names[int(box.cls[0])]

        # Clamp coordinates to frame bounds
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = min(w, x2); y2 = min(h, y2)

        # Depth: use bottom 40% of bounding box (ground contact area — more accurate)
        y_ground  = int(y1 + 0.6 * (y2 - y1))
        roi_depth = depth_map[y_ground:y2, x1:x2]
        avg_depth = float(np.median(roi_depth)) if roi_depth.size > 0 else 128.0

        distance_m = midas_to_meters(avg_depth)
        distance_m = round(distance_m, 2)

        # Zone assignment
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        zone     = get_zone(center_x, w)
        v_zone   = get_vertical_zone(center_y, h)

        # Risk score
        priority = PRIORITY_WEIGHTS.get(label, 3.0)
        proximity = min(1.0, 2.0 / (distance_m + 0.1))   # closer = higher
        v_mult    = {"bottom": 2.0, "middle": 1.2, "top": 0.7}[v_zone]
        risk      = priority * proximity * v_mult

        zone_risks[zone] = max(zone_risks[zone], risk)

        # Danger flag (same logic as your original beep trigger)
        if 0 < distance_m < DANGER_DISTANCE_M:
            danger_found = True

        detections.append({
            "label":        label,
            "confidence":   round(conf, 2),
            "distance_m":   distance_m,
            "zone":         zone,
            "vertical":     v_zone,
            "risk":         round(risk, 2),
            "bbox":         [x1, y1, x2, y2],
        })

    # Sort by distance for cleaner output
    detections.sort(key=lambda d: d["distance_m"])

    nav_result = nav_engine.process(detections, zone_risks)
    latency_ms = round((time.time() - start_time) * 1000, 1)

    return {
        "detections":     detections,
        "zone_risks":     {k: round(v, 2) for k, v in zone_risks.items()},
        "danger":         danger_found,
        "latency_ms":     latency_ms,
        "frame_size":     [w, h],
        "voice_message":  nav_result["voice_message"],
        "priority":       nav_result["priority"],
        "should_speak":   nav_result["should_speak"],
        "alert_type":     nav_result["alert_type"],
        "alert_pattern":  nav_result["alert_pattern"],
        "alert_duration": nav_result["alert_duration"],
        "safe_direction": nav_result["safe_direction"],
        "safe_zone":      nav_result["safe_zone"],
    }


# ─────────────────────────────────────────────
#  FLASK ROUTES
# ─────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Quick check — open this in phone browser to verify connection"""
    return jsonify({
        "status":  "running",
        "models":  "YOLOv8n + MiDaS_small",
        "message": "Smart Path Suggestor server is ready."
    })


@app.route("/detect", methods=["POST"])
def detect():
    """
    Main detection endpoint.

    Expects JSON body:
    {
        "image": "<base64 encoded JPEG string>"
    }

    Returns JSON:
    {
        "detections":    [...],
        "zone_risks":    {"left": 0.0, "center": 2.4, "right": 0.8},
        "danger":        true/false,
        "voice_message": "Person 1.2 meters ahead. Slow down.",
        "latency_ms":    145.3
    }
    """
    # ── Validate request ──────────────────────────────────────
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if "image" not in data:
        return jsonify({"error": "Missing 'image' field in JSON body"}), 400

    # ── Decode image ──────────────────────────────────────────
    try:
        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Could not decode image"}), 400
    except Exception as e:
        return jsonify({"error": f"Image decode failed: {str(e)}"}), 400

    # ── Resize for performance (same as your original code) ───
    frame = cv2.resize(frame, (480, 360))

    # ── Run detection pipeline ────────────────────────────────
    try:
        result = run_detection(frame)
    except Exception as e:
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

    return jsonify(result)


@app.route("/", methods=["GET"])
def mobile_client():
    """Serve the mobile web client directly from the server"""
    return send_file("mobile_client.html")


# ─────────────────────────────────────────────
#  START SERVER
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import socket

    # Reliably find WiFi IP by connecting a dummy UDP socket
    # This picks the interface your laptop uses to reach the network
    def get_wifi_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))   # Google DNS — no data actually sent
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    local_ip = get_wifi_ip()

    print("\n" + "=" * 50)
    print("  🚀 Server running!")
    print(f"  Local IP:   http://{local_ip}:5000")
    print(f"  Health:     http://{local_ip}:5000/health")
    print(f"  Mobile app: http://{local_ip}:5000/")
    print("  Open the Mobile app URL on your phone browser")
    print()
    print("  📱 To enable camera on phone:")
    print("     1. Open Chrome → type  chrome://flags")
    print("     2. Search: 'insecure origins'")
    print("     3. Add:  http://" + local_ip + ":5000")
    print("     4. Tap 'Relaunch' → then open the URL above")
    print("=" * 50 + "\n")

    app.run(
        host="0.0.0.0",   # Accept connections from any device on network
        port=5000,
        debug=False,       # Keep False — debug mode reloads models twice
        threaded=True      # Handle multiple requests simultaneously
    )
