import os
import base64
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, send_file
from src.vision_safety.detector import run_detection, yolo_models

api_blueprint = Blueprint('api', __name__)

def decode_base64_image(b64_string):
    img_bytes = base64.b64decode(b64_string)
    img_array = np.frombuffer(img_bytes, np.uint8)
    frame     = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return frame

@api_blueprint.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":  "running",
        "models":  list(yolo_models.keys()),
        "depth_model": "MiDaS_small",
        "message": "Smart Path Suggestor server is ready."
    })

@api_blueprint.route("/detect", methods=["POST"])
def detect():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    if "image" not in data:
        return jsonify({"error": "Missing 'image' field"}), 400

    try:
        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Could not decode image"}), 400
    except Exception as e:
        return jsonify({"error": f"Image decode failed: {str(e)}"}), 400

    frame = cv2.resize(frame, (480, 360))
    model_key = data.get("model", "yolov8n")

    try:
        result = run_detection(frame, model_key=model_key)
        result["model_used"] = model_key
    except Exception as e:
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

    return jsonify(result)

@api_blueprint.route("/", methods=["GET"])
def mobile_client():
    client_html_path = os.path.join(os.path.dirname(__file__), "..", "..", "client", "mobile_client.html")
    return send_file(os.path.abspath(client_html_path))
