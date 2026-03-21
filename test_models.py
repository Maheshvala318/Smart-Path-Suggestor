import requests
import base64
import json
import os

# Create a small dummy image for testing
try:
    import cv2
    import numpy as np
    dummy_img = np.zeros((360, 480, 3), dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', dummy_img)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
except ImportError:
    # If cv2 not available, use a minimal base64 JPEG header
    img_b64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAKAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZnaGlqc3R1dnd4eXqGhcXHyMnkyicPExWElGZYSXJnZ1hWZnJlbm9lZ3R1dnd4eXp7fH1+f3OEhYaHiImKkpOUlZaXmJmqrawp audition/"

SERVER_URL = "http://localhost:5000"

def test_model(model_name):
    print(f"\nTesting model: {model_name}")
    payload = {
        "image": img_b64,
        "model": model_name
    }
    try:
        response = requests.post(f"{SERVER_URL}/detect", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Server used model: {result.get('model_used')}")
            print(f"Latency: {result.get('latency_ms')}ms")
            return True
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Check health first
    try:
        health = requests.get(f"{SERVER_URL}/health", timeout=5).json()
        print(f"Server Health: {health}")
    except:
        print("❌ Server not running. Please start server.py first.")
        exit(1)

    test_model("yolov8n")
    test_model("best")
    test_model("invalid") # Should fall back to default
