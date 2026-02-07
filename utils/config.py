"""
OcuLink-AI Configuration Module
Settings for camera, facial landmark thresholds, and gesture timing.
"""

# ── CAMERA SETTINGS ──────────────────────────────────────────────
# 0: Default Integrated Webcam | 1+: External/Android Webcams
CAMERA_INDEX = 0 

# ── HEAD POSE SETTINGS ───────────────────────────────────────────
# Higher = requires a further head turn (less sensitive)
# Lower  = easier to trigger (more sensitive)
YAW_THRESHOLD = 0.45

# ── EYE ASPECT RATIO (EAR) SETTINGS ──────────────────────────────
# Standard Open Eye EAR: 0.25 - 0.35
# Standard Closed Eye EAR: < 0.20
EYE_CONFIG = {
    "LEFT_THRESHOLD": 0.22,    # Sensitivity for left eye
    "RIGHT_THRESHOLD": 0.22,   # Sensitivity for right eye
    "CONSEC_FRAMES": 4         # Frames the eye must be closed to trigger
}

"""
TUNING GUIDE FOR EYES:
- Natural blinks triggering actions? -> Increase CONSEC_FRAMES to 6.
- Winks not detecting?               -> Decrease THRESHOLD to 0.19.
- Glasses causing false triggers?    -> Decrease THRESHOLD to 0.17.
"""

# ── EYEBROW SETTINGS ──────────────────────────────────────────────
# Distance between eye top and eyebrow
BROW_CONFIG = {
    "RAISE_THRESHOLD": 0.070,  # Normalized distance trigger
    "HOLD_FRAMES": 30          # Required hold duration (~1.0s @ 30fps)
}

# ── KEYBOARD COOLDOWN ─────────────────────────────────────────────
# Prevents a single gesture from spamming multiple key presses
GLOBAL_COOLDOWN = 0.6