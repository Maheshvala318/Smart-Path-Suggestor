import cv2
import torch
import numpy as np
import winsound
import time
from ultralytics import YOLO

# -------------------------
# Load YOLO
# -------------------------
model = YOLO("yolov8n.pt")

# -------------------------
# Load MiDaS
# -------------------------
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", trust_repo=True)
midas.eval()

midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
transform = midas_transforms.small_transform

device = torch.device("cpu")
midas.to(device)

# -------------------------
# Calibration
# -------------------------
KNOWN_DISTANCE_M = 2.0
MIDAS_VALUE_AT_KNOWN = 142
SCALE = KNOWN_DISTANCE_M * MIDAS_VALUE_AT_KNOWN

def midas_to_meters(depth_value):
    return SCALE / (depth_value + 1e-6)

# -------------------------
# Camera Setup
# -------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

frame_count = 0
cached_boxes = []
cached_depth_map = None

# Beep control
last_beep_time = 0
BEEP_COOLDOWN = 1.0   # seconds
BEEP_DISTANCE = 0.5   # meters threshold

print("Press q to exit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame = cv2.resize(frame, (480, 360))
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ---------------------------------
    # Run heavy models every 8 frames
    # ---------------------------------
    if frame_count % 8 == 0:

        # YOLO
        results = model(frame, imgsz=480, verbose=False)
        cached_boxes = results[0].boxes

        # MiDaS
        input_batch = transform(img_rgb).to(device)
        with torch.no_grad():
            prediction = midas(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bilinear",
                align_corners=False,
            ).squeeze()
        cached_depth_map = prediction.cpu().numpy()

    # ---------------------------------
    # Draw + Check Distance
    # ---------------------------------
    danger_detected = False

    if cached_boxes is not None and cached_depth_map is not None:
        for box in cached_boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]

            object_depth = cached_depth_map[y1:y2, x1:x2]

            if object_depth.size > 0:
                avg_depth = float(np.mean(object_depth))
                distance_m = midas_to_meters(avg_depth)
            else:
                distance_m = 0

            # Check danger
            if 0 < distance_m < BEEP_DISTANCE:
                danger_detected = True

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(
                frame,
                f"{label} {distance_m:.2f}m",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,0),
                2
            )

    # ---------------------------------
    # Beep Alert
    # ---------------------------------
    current_time = time.time()
    if danger_detected and (current_time - last_beep_time > BEEP_COOLDOWN):
        winsound.Beep(1000, 300)   # frequency, duration
        last_beep_time = current_time

    cv2.imshow("Smart Path - Beep Alert", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()