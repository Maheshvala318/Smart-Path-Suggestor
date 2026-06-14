import time
import collections
import numpy as np

from src.core.config import (
    DIST_CRITICAL, DIST_DANGER, DIST_WARN, DIST_CLEAR,
    DETECTION_STABILITY_FRAMES, ZONE_SMOOTHING_FRAMES, COOLDOWN,
    PRIORITY_WEIGHTS as RISK_WEIGHTS, VOICE_LABELS, ZONE_VOICE,
    ZONE_AVOID, REGION_LABELS, MAX_PRIORITY_BY_REGION, PRIORITY_RANK
)

class ObjectTracker:
    def __init__(self, stability_frames=DETECTION_STABILITY_FRAMES):
        self.stability_frames = stability_frames
        self.history   = collections.defaultdict(
            lambda: collections.deque(maxlen=stability_frames)
        )
        self.last_seen = {}

    def update(self, detections):
        current_time = time.time()
        current_keys = set()

        for det in detections:
            key = f"{det['label']}_{det['zone']}"
            current_keys.add(key)

            self.history[key].append({
                "label":      det["label"],
                "distance_m": det["distance_m"],
                "zone":       det["zone"],
                "region":     det.get("region", 0),
                "confidence": det["confidence"],
                "risk":       det["risk"],
            })
            self.last_seen[key] = current_time

        stale = [k for k, t in self.last_seen.items() if current_time - t > 2.0]
        for k in stale:
            del self.history[k]
            del self.last_seen[k]

        stable = []
        for key, frames in self.history.items():
            if len(frames) >= self.stability_frames:
                avg_dist = np.mean([f["distance_m"] for f in frames])
                latest   = frames[-1].copy()
                latest["distance_m"] = round(float(avg_dist), 2)
                stable.append(latest)

        return stable

class ZoneSmoother:
    def __init__(self, smoothing_frames=ZONE_SMOOTHING_FRAMES):
        self.smoothing_frames = smoothing_frames
        self.zone_history     = collections.deque(maxlen=smoothing_frames)
        self.current_zone     = "center"

    def update(self, zone_risks: dict) -> str:
        safest = min(zone_risks, key=zone_risks.get)
        self.zone_history.append(safest)

        if len(self.zone_history) < self.smoothing_frames:
            return safest

        counts        = collections.Counter(self.zone_history)
        majority_zone = counts.most_common(1)[0][0]
        majority_ratio = counts[majority_zone] / self.smoothing_frames

        if majority_ratio >= 0.6:
            self.current_zone = majority_zone

        return self.current_zone

class SituationState:
    def __init__(self):
        self.last_message_time = {}
        self.last_message_text = {}

    def should_speak(self, priority, message_text):
        now      = time.time()
        cooldown = COOLDOWN.get(priority, 5.0)
        last_time = self.last_message_time.get(priority, 0)
        last_text = self.last_message_text.get(priority, "")

        if message_text != last_text:
            return True
        if now - last_time >= cooldown:
            return True

        return False

    def mark_spoken(self, priority, message_text):
        self.last_message_time[priority] = time.time()
        self.last_message_text[priority] = message_text

class NavigationEngine:
    def __init__(self):
        self.tracker      = ObjectTracker()
        self.smoother     = ZoneSmoother()
        self.state        = SituationState()
        self.frame_count  = 0

    def process(self, raw_detections: list, zone_risks: dict) -> dict:
        self.frame_count += 1
        stable_dets = self.tracker.update(raw_detections)
        safe_zone = self.smoother.update(zone_risks)
        threat = self._get_primary_threat(stable_dets)
        priority = self._get_priority(threat)
        message = self._build_message(threat, safe_zone, zone_risks, stable_dets)

        speak_now = self.state.should_speak(priority, message)
        if speak_now:
            self.state.mark_spoken(priority, message)

        alert = self._get_alert(priority, threat)
        safe_dir = self._get_safe_direction(zone_risks, threat)

        return {
            "voice_message":  message,
            "priority":       priority,
            "should_speak":   speak_now,
            "alert_type":     alert["type"],
            "alert_pattern":  alert["pattern"],
            "alert_duration": alert["duration"],
            "beep_side":      alert.get("beep_side", "center"),
            "safe_direction": safe_dir,
            "safe_zone":      safe_zone,
            "stable_count":   len(stable_dets),
            "threat":         threat,
        }

    def _get_primary_threat(self, stable_dets):
        if not stable_dets:
            return None

        def threat_score(det):
            weight    = RISK_WEIGHTS.get(det["label"], 3.0)
            proximity = 1.0 / (det["distance_m"] + 0.1)
            region    = det.get("region", 0)
            region_mult = {0: 3.0, -1: 1.2, 1: 1.2, -2: 0.5, 2: 0.5}.get(region, 1.0)
            return weight * proximity * region_mult

        return max(stable_dets, key=threat_score)

    def _get_priority(self, threat):
        if threat is None:
            return "CLEAR"

        dist      = threat["distance_m"]
        obj       = threat["label"]
        region    = threat.get("region", 0)
        high_risk = obj in ["pothole", "stair_down", "step_down", "car", "truck", "bus", "motorcycle"]

        if obj == "wall":
            if dist <= 1.0:
                raw_priority = "CRITICAL"
            else:
                raw_priority = "GUIDE"
        elif dist <= DIST_CRITICAL or (high_risk and dist <= DIST_DANGER):
            raw_priority = "CRITICAL"
        elif dist <= DIST_DANGER:
            raw_priority = "DANGER"
        elif dist <= DIST_WARN:
            raw_priority = "WARN"
        else:
            raw_priority = "GUIDE"

        abs_region = abs(region)
        max_allowed = MAX_PRIORITY_BY_REGION.get(abs_region, "GUIDE")
        raw_rank = PRIORITY_RANK.get(raw_priority, 0)
        max_rank = PRIORITY_RANK.get(max_allowed, 0)

        if raw_rank > max_rank:
            return max_allowed
        return raw_priority

    def _build_message(self, threat, safe_zone, zone_risks, stable_dets):
        if threat is None:
            return "Path is clear."

        dist     = threat["distance_m"]
        region   = threat.get("region", 0)
        label    = VOICE_LABELS.get(threat["label"], threat["label"])
        zone_str = ZONE_VOICE.get(region, "ahead")
        priority = self._get_priority(threat)

        if abs(region) >= 2:
            return f"{label.capitalize()} {zone_str}."

        if abs(region) == 1:
            return f"{label.capitalize()} {zone_str}, {dist:.1f} meters."

        if priority == "CRITICAL":
            if threat["label"] in ["stair_down", "step_down"]:
                return f"Warning! {label} {zone_str}. Stop and be careful."
            if threat["label"] in ["car", "truck", "bus", "motorcycle"]:
                return f"Vehicle {zone_str}! Stop immediately."
            if threat["label"] == "pothole":
                avoid = ZONE_AVOID.get(region, "Stop")
                return f"Pothole {zone_str}! {avoid}."
            return f"Stop! {label} {int(dist * 100)} centimeters ahead."

        elif priority == "DANGER":
            if threat["label"] in ["stair_down", "step_down"]:
                return f"Steps going down {zone_str}. Slow down."
            if threat["label"] in ["stair_up", "step_up"]:
                return f"Steps going up {zone_str}. Watch your step."
            return f"{label.capitalize()} ahead, {dist:.1f} meters. Slow down."

        elif priority == "WARN":
            if len(stable_dets) > 2:
                return "Multiple obstacles ahead. Walk carefully."
            return f"{label.capitalize()} ahead, {dist:.1f} meters."

        else:
            direction_messages = {
                -2: "Move left, path is clearer.",
                -1: "Slight left, path is clearer.",
                 0: "Walk straight, path ahead is clear.",
                 1: "Slight right, path is clearer.",
                 2: "Move right, path is clearer.",
            }
            return direction_messages.get(safe_zone, "Walk carefully.")

    def _get_alert(self, priority, threat=None):
        region = threat.get("region", 0) if threat else 0
        abs_region = abs(region)

        if region < 0:
            beep_side = "left"
        elif region > 0:
            beep_side = "right"
        else:
            beep_side = "center"

        if abs_region >= 2:
            return {"type": "beep", "pattern": [], "duration": 0, "beep_side": beep_side}

        if abs_region == 1:
            return {"type": "beep", "pattern": [100], "duration": 100, "beep_side": beep_side}

        patterns = {
            "CRITICAL": {"type": "vibrate", "pattern": [300, 100, 300, 100, 300], "duration": 900, "beep_side": "center"},
            "DANGER": {"type": "vibrate", "pattern": [200, 100, 200], "duration": 500, "beep_side": "center"},
            "WARN": {"type": "vibrate", "pattern": [150], "duration": 150, "beep_side": "center"},
            "GUIDE": {"type": "none", "pattern": [], "duration": 0, "beep_side": "center"},
            "CLEAR": {"type": "none", "pattern": [], "duration": 0, "beep_side": "center"},
        }
        return patterns.get(priority, patterns["CLEAR"])

    def _get_safe_direction(self, zone_risks, threat):
        if not zone_risks:
            return "straight"

        safest_region = min(zone_risks, key=zone_risks.get)
        min_risk      = zone_risks[safest_region]

        if min_risk >= 8.0:
            return "stop"

        direction_map = {-2: "left", -1: "slight left", 0: "straight", 1: "slight right", 2: "right"}
        return direction_map.get(safest_region, "straight")
