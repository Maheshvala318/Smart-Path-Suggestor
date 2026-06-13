import cv2
import numpy as np
import json
import os

img_path = r'd:\Project\Smart Path Suggestor\image data.png'
img = cv2.imread(img_path)

if img is None:
    print("Could not read image")
    exit()

# Convert to HSV to easily select red
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
mask1 = cv2.inRange(hsv, lower_red1, upper_red1)

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

mask_red = mask1 + mask2

contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

nodes = []
for idx, c in enumerate(contours):
    # Calculate moment to find center
    M = cv2.moments(c)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        nodes.append({"id": f"node_{idx}", "x": cX, "y": cY})
        
# Sort nodes primarily by x, then y
nodes.sort(key=lambda n: (n['x'], n['y']))

with open("red_dots.json", "w") as f:
    json.dump(nodes, f, indent=2)

print(f"Extracted {len(nodes)} red dots.")
