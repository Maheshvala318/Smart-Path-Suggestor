# ============================================================
#  navigation_engine.py
#  Smart navigation logic — handles voice messages, alerts,
#  zone smoothing, state tracking, and priority queuing.
#
#  Import this in server.py:
#      from navigation_engine import NavigationEngine
# ============================================================

import time
import collections
import numpy as np


# ─────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────

# Distance bands in meters
DIST_CRITICAL = 3.0    # STOP immediately
DIST_DANGER   = 5.0    # slow down
DIST_WARN     = 7.0    # early warning
DIST_CLEAR    = 9.0    # safe, no alert

# Object must appear in this many consecutive frames before alert
DETECTION_STABILITY_FRAMES = 3

# Zone smoothing window
ZONE_SMOOTHING_FRAMES = 5

# Cooldown in seconds — how long before same message repeats
COOLDOWN = {
    "CRITICAL": 2.0,
    "DANGER":   4.0,
    "WARN":     6.0,
    "GUIDE":    8.0,
    "CLEAR":   10.0,
}

# Risk weights per object class
RISK_WEIGHTS = {
    "person":      7.0,
    "car":        10.0,
    "truck":      10.0,
    "bus":        10.0,
    "motorcycle":  9.0,
    "bicycle":     6.0,
    "dog":         8.0,
    "cat":         4.0,
    "pothole":     9.0,
    "stair_down":  9.5,
    "stair_up":    5.0,
    "step_down":   9.0,
    "step_up":     5.0,
    "bump":        7.0,
    "pole":        4.0,
    "tree":        3.0,
    "chair":       3.0,
    "bench":       2.0,
}

# Human-friendly label names for voice output
VOICE_LABELS = {
    "person":     "person",
    "car":        "vehicle",
    "truck":      "truck",
    "bus":        "bus",
    "motorcycle": "motorcycle",
    "bicycle":    "bicycle",
    "dog":        "dog",
    "pothole":    "pothole",
    "stair_down": "steps going down",
    "stair_up":   "steps going up",
    "step_down":  "step down",
    "step_up":    "step up",
    "bump":       "speed bump",
    "pole":       "pole",
    "tree":       "tree",
}

# Zone names for voice output (numeric regions)
ZONE_VOICE = {
    -2: "on your left",
    -1: "slightly left",
     0: "directly ahead",
     1: "slightly right",
     2: "on your right",
}

# What to do when a zone is dangerous
ZONE_AVOID = {
    -2: "Move right",
    -1: "Move slightly right",
     0: "Stop",
     1: "Move slightly left",
     2: "Move left",
}

# Region labels for display
REGION_LABELS = {
    -2: "left",
    -1: "center_left",
     0: "center",
     1: "center_right",
     2: "right",
}

# Maximum priority allowed per region abs-value
# Region 0 (center) = full alerts,  ±1 = max WARN,  ±2 = max GUIDE
MAX_PRIORITY_BY_REGION = {
    0: "CRITICAL",   # center path: full alerts
    1: "WARN",       # near-path:  reduced, short beep
    2: "GUIDE",      # off-path:   detect only, minimal beep
}

# Priority rank for capping comparison
PRIORITY_RANK = {
    "CLEAR": 0,
    "GUIDE": 1,
    "WARN": 2,
    "DANGER": 3,
    "CRITICAL": 4,
}


# ─────────────────────────────────────────────────────────────
#  CLASS 1 — OBJECT TRACKER
#  Filters out unstable single-frame detections
# ─────────────────────────────────────────────────────────────

class ObjectTracker:
    """
    Tracks objects across frames.
    An object is only confirmed after appearing in N consecutive frames.
    Eliminates false positives from single noisy frames.
    """

    def __init__(self, stability_frames=DETECTION_STABILITY_FRAMES):
        self.stability_frames = stability_frames
        # key = "label_zone", value = deque of recent detections
        self.history   = collections.defaultdict(
            lambda: collections.deque(maxlen=stability_frames)
        )
        self.last_seen = {}

    def update(self, detections):
        """
        Feed current frame detections.
        Returns only STABLE detections (seen in N consecutive frames).
        """
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

        # Remove objects not seen for more than 2 seconds
        stale = [k for k, t in self.last_seen.items()
                 if current_time - t > 2.0]
        for k in stale:
            del self.history[k]
            del self.last_seen[k]

        # Return only stable detections (seen in enough frames)
        stable = []
        for key, frames in self.history.items():
            if len(frames) >= self.stability_frames:
                # Average distance over stable frames for smoothness
                avg_dist = np.mean([f["distance_m"] for f in frames])
                latest   = frames[-1].copy()
                latest["distance_m"] = round(float(avg_dist), 2)
                stable.append(latest)

        return stable


# ─────────────────────────────────────────────────────────────
#  CLASS 2 — ZONE SMOOTHER
#  Prevents left/center/left flickering at zone boundaries
# ─────────────────────────────────────────────────────────────

class ZoneSmoother:
    """
    Smooths zone assignment over multiple frames using majority vote.
    Uses hysteresis — once in a zone, needs strong evidence to leave.

    Example without smoother:
      Frame 1: object at 39% → center_left
      Frame 2: object at 41% → center
      Frame 3: object at 39% → center_left
      Voice: "slightly left... ahead... slightly left..." (confusing)

    Example with smoother:
      Frames 1-5: majority = center_left
      Voice: "slightly left" (stable, one message)
    """

    def __init__(self, smoothing_frames=ZONE_SMOOTHING_FRAMES):
        self.smoothing_frames = smoothing_frames
        self.zone_history     = collections.deque(maxlen=smoothing_frames)
        self.current_zone     = "center"

    def update(self, zone_risks: dict) -> str:
        """
        Input:  zone_risks dict {"left": 2.1, "center": 5.4, ...}
        Output: smoothed safest zone string
        """
        safest = min(zone_risks, key=zone_risks.get)
        self.zone_history.append(safest)

        if len(self.zone_history) < self.smoothing_frames:
            return safest

        # Majority vote over last N frames
        counts        = collections.Counter(self.zone_history)
        majority_zone = counts.most_common(1)[0][0]
        majority_ratio = counts[majority_zone] / self.smoothing_frames

        # Only change zone if new zone clearly dominates (60% threshold)
        if majority_ratio >= 0.6:
            self.current_zone = majority_zone

        return self.current_zone


# ─────────────────────────────────────────────────────────────
#  CLASS 3 — SITUATION STATE
#  Controls when to speak based on change detection + cooldowns
# ─────────────────────────────────────────────────────────────

class SituationState:
    """
    Tracks the current navigation situation.
    Only allows speaking when:
      1. Message is different from last spoken message, OR
      2. Cooldown time has passed for this priority level

    This prevents the same message repeating 20 times in 10 seconds.
    """

    def __init__(self):
        self.last_message_time = {}
        self.last_message_text = {}

    def should_speak(self, priority, message_text):
        """
        Returns True if this message should be spoken right now.
        """
        now      = time.time()
        cooldown = COOLDOWN.get(priority, 5.0)

        last_time = self.last_message_time.get(priority, 0)
        last_text = self.last_message_text.get(priority, "")

        # Always speak if message is different from last time
        if message_text != last_text:
            return True

        # Repeat same message only after cooldown period
        if now - last_time >= cooldown:
            return True

        return False

    def mark_spoken(self, priority, message_text):
        """Call this after deciding to speak a message."""
        self.last_message_time[priority] = time.time()
        self.last_message_text[priority] = message_text


# ─────────────────────────────────────────────────────────────
#  CLASS 4 — NAVIGATION ENGINE  (main class)
#  Orchestrates all the above + builds messages + alerts
# ─────────────────────────────────────────────────────────────

class NavigationEngine:
    """
    Main navigation brain. Call process() every frame.

    Usage in server.py:
        engine = NavigationEngine()   # create once at startup

        # inside run_detection():
        result = engine.process(detections, zone_risks)

    result contains:
        voice_message   what to say
        priority        CRITICAL / DANGER / WARN / GUIDE / CLEAR
        should_speak    True/False — mobile client obeys this
        alert_type      "vibrate" / "none"
        alert_pattern   list of ms values for vibration e.g. [300,100,300]
        alert_duration  total ms of vibration
        safe_direction  "straight" / "left" / "right" / "stop"
        safe_zone       "center" / "center_left" etc
        stable_count    number of stable detections this frame
        threat          primary threat detection dict or None
    """

    def __init__(self):
        self.tracker      = ObjectTracker()
        self.smoother     = ZoneSmoother()
        self.state        = SituationState()
        self.frame_count  = 0

    def process(self, raw_detections: list, zone_risks: dict) -> dict:
        """
        Full processing pipeline for one frame.
        Call this every time server receives a frame from phone.
        """
        self.frame_count += 1

        # Step 1: Stabilize — filter out single-frame noise
        stable_dets = self.tracker.update(raw_detections)

        # Step 2: Smooth — prevent zone flickering
        safe_zone = self.smoother.update(zone_risks)

        # Step 3: Find the single most dangerous threat
        threat = self._get_primary_threat(stable_dets)

        # Step 4: Assign priority level to this threat
        priority = self._get_priority(threat)

        # Step 5: Build voice message
        message = self._build_message(threat, safe_zone, zone_risks, stable_dets)

        # Step 6: Decide if we should speak right now
        speak_now = self.state.should_speak(priority, message)
        if speak_now:
            self.state.mark_spoken(priority, message)

        # Step 7: Build vibration alert (region-aware)
        alert = self._get_alert(priority, threat)

        # Step 8: Safe direction for arrow display
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

    # ─────────────────────────────────────────────────────────
    #  PRIVATE METHODS
    # ─────────────────────────────────────────────────────────

    def _get_primary_threat(self, stable_dets):
        """
        From all stable detections, find the single most dangerous one.
        Score = risk_weight x distance_proximity x region_multiplier
        Region 0 (center) is heavily prioritized — user walks into it.
        Side regions are down-weighted so they don't dominate.
        """
        if not stable_dets:
            return None

        def threat_score(det):
            weight    = RISK_WEIGHTS.get(det["label"], 3.0)
            proximity = 1.0 / (det["distance_m"] + 0.1)
            region    = det.get("region", 0)
            # Center gets 3x, near-sides 1.2x, far-sides 0.5x
            region_mult = {0: 3.0, -1: 1.2, 1: 1.2, -2: 0.5, 2: 0.5}.get(region, 1.0)
            return weight * proximity * region_mult

        return max(stable_dets, key=threat_score)

    def _get_priority(self, threat):
        """
        Map threat properties to a priority level.
        High-risk objects (pothole, stair_down, vehicle) escalate earlier.

        REGION-AWARE: priority is capped by region.
        Region 0 (center) → full CRITICAL/DANGER/WARN
        Region ±1 (near-side) → max WARN
        Region ±2 (far-side) → max GUIDE
        """
        if threat is None:
            return "CLEAR"

        dist      = threat["distance_m"]
        obj       = threat["label"]
        region    = threat.get("region", 0)
        high_risk = obj in [
            "pothole", "stair_down", "step_down",
            "car", "truck", "bus", "motorcycle"
        ]

        # Compute raw priority based on distance
        if dist <= DIST_CRITICAL or (high_risk and dist <= DIST_DANGER):
            raw_priority = "CRITICAL"
        elif dist <= DIST_DANGER:
            raw_priority = "DANGER"
        elif dist <= DIST_WARN:
            raw_priority = "WARN"
        else:
            raw_priority = "GUIDE"

        # Cap priority based on region
        abs_region = abs(region)
        max_allowed = MAX_PRIORITY_BY_REGION.get(abs_region, "GUIDE")
        raw_rank = PRIORITY_RANK.get(raw_priority, 0)
        max_rank = PRIORITY_RANK.get(max_allowed, 0)

        if raw_rank > max_rank:
            # Downgrade: side objects shouldn't trigger critical
            return max_allowed
        return raw_priority

    def _build_message(self, threat, safe_zone, zone_risks, stable_dets):
        """
        Build natural voice message based on priority + threat + context.
        Region-aware: center objects get urgent messages, side objects
        get brief descriptions, far-side objects get no voice (beep only).
        """

        # No threats at all
        if threat is None:
            return "Path is clear."

        dist     = threat["distance_m"]
        region   = threat.get("region", 0)
        label    = VOICE_LABELS.get(threat["label"], threat["label"])
        zone_str = ZONE_VOICE.get(region, "ahead")
        priority = self._get_priority(threat)

        # ── FAR SIDE (region ±2): no voice, beep only ─────────
        if abs(region) >= 2:
            # No voice message for far-side objects, just beep
            return f"{label.capitalize()} {zone_str}."

        # ── NEAR SIDE (region ±1): brief description ──────────
        if abs(region) == 1:
            return f"{label.capitalize()} {zone_str}, {dist:.1f} meters."

        # ── CENTER (region 0): full detailed messages ─────────

        # ── CRITICAL ──────────────────────────────────────────
        if priority == "CRITICAL":

            if threat["label"] in ["stair_down", "step_down"]:
                return f"Warning! {label} {zone_str}. Stop and be careful."

            if threat["label"] in ["car", "truck", "bus", "motorcycle"]:
                return f"Vehicle {zone_str}! Stop immediately."

            if threat["label"] == "pothole":
                avoid = ZONE_AVOID.get(region, "Stop")
                return f"Pothole {zone_str}! {avoid}."

            return f"Stop! {label} {int(dist * 100)} centimeters ahead."

        # ── DANGER ────────────────────────────────────────────
        elif priority == "DANGER":

            if threat["label"] in ["stair_down", "step_down"]:
                return f"Steps going down {zone_str}. Slow down."

            if threat["label"] in ["stair_up", "step_up"]:
                return f"Steps going up {zone_str}. Watch your step."

            return f"{label.capitalize()} ahead, {dist:.1f} meters. Slow down."

        # ── WARN ──────────────────────────────────────────────
        elif priority == "WARN":

            # Multiple objects — give summary instead of listing all
            if len(stable_dets) > 2:
                return "Multiple obstacles ahead. Walk carefully."

            return f"{label.capitalize()} ahead, {dist:.1f} meters."

        # ── GUIDE — objects far away, suggest direction ────────
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
        """
        Returns vibration pattern + beep info for phone.
        Region-aware:
          - Region 0 (center): full vibration patterns
          - Region ±1: short single vibration + beep
          - Region ±2: minimal beep only (no vibration)
        beep_side tells the client which tone to play:
          "left" = low frequency, "right" = high frequency, "center" = no beep
        """
        region = threat.get("region", 0) if threat else 0
        abs_region = abs(region)

        # Determine beep side: negative regions = left, positive = right
        if region < 0:
            beep_side = "left"
        elif region > 0:
            beep_side = "right"
        else:
            beep_side = "center"

        # ── Region ±2 (far side): minimal beep, no vibration ──
        if abs_region >= 2:
            return {
                "type": "beep",
                "pattern": [],
                "duration": 0,
                "beep_side": beep_side,
            }

        # ── Region ±1 (near side): short vibration + beep ──
        if abs_region == 1:
            return {
                "type": "beep",
                "pattern": [100],   # single short pulse
                "duration": 100,
                "beep_side": beep_side,
            }

        # ── Region 0 (center path): full alerts ──
        patterns = {
            "CRITICAL": {
                "type":      "vibrate",
                "pattern":   [300, 100, 300, 100, 300],  # 3 strong pulses
                "duration":  900,
                "beep_side": "center",
            },
            "DANGER": {
                "type":      "vibrate",
                "pattern":   [200, 100, 200],             # 2 medium pulses
                "duration":  500,
                "beep_side": "center",
            },
            "WARN": {
                "type":      "vibrate",
                "pattern":   [150],                       # 1 short pulse
                "duration":  150,
                "beep_side": "center",
            },
            "GUIDE": {
                "type":      "none",
                "pattern":   [],
                "duration":  0,
                "beep_side": "center",
            },
            "CLEAR": {
                "type":      "none",
                "pattern":   [],
                "duration":  0,
                "beep_side": "center",
            },
        }
        return patterns.get(priority, patterns["CLEAR"])

    def _get_safe_direction(self, zone_risks, threat):
        """
        Returns simplest walking direction based on zone risks.
        Uses numeric regions.
        """
        if not zone_risks:
            return "straight"

        safest_region = min(zone_risks, key=zone_risks.get)
        min_risk      = zone_risks[safest_region]

        if min_risk >= 8.0:
            return "stop"   # All zones very dangerous

        direction_map = {
            -2: "left",
            -1: "slight left",
             0: "straight",
             1: "slight right",
             2: "right",
        }
        return direction_map.get(safest_region, "straight")
