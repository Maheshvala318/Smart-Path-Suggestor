import collections

# Distance bands in meters
DIST_CRITICAL = 3.0
DIST_DANGER   = 5.0
DIST_WARN     = 7.0
DIST_CLEAR    = 9.0

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.30

# MiDaS calibration
KNOWN_DISTANCE_M     = 2.0
MIDAS_VALUE_AT_KNOWN = 142
SCALE                = 775

# Object priority weights for risk scoring
PRIORITY_WEIGHTS = {
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
    "chair":       4.0,
    "bench":       2.0,
    "wall":        5.0,
}

# Detection filtering
DETECTION_STABILITY_FRAMES = 3
ZONE_SMOOTHING_FRAMES = 5

COOLDOWN = {
    "CRITICAL": 2.0,
    "DANGER":   4.0,
    "WARN":     6.0,
    "GUIDE":    8.0,
    "CLEAR":   10.0,
}

# Labels map
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
    "wall":       "wall",
}

ZONE_VOICE = {
    -2: "on your left",
    -1: "slightly left",
     0: "directly ahead",
     1: "slightly right",
     2: "on your right",
}

ZONE_AVOID = {
    -2: "Move right",
    -1: "Move slightly right",
     0: "Stop",
     1: "Move slightly left",
     2: "Move left",
}

REGION_LABELS = {
    -2: "left",
    -1: "center_left",
     0: "center",
     1: "center_right",
     2: "right",
}

MAX_PRIORITY_BY_REGION = {
    0: "CRITICAL",
    1: "WARN",
    2: "GUIDE",
}

PRIORITY_RANK = {
    "CLEAR": 0,
    "GUIDE": 1,
    "WARN": 2,
    "DANGER": 3,
    "CRITICAL": 4,
}
