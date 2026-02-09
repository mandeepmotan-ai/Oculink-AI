import numpy as np
from collections import deque
from utils.config import SMILE_THRESHOLD, SMILE_HOLD_FRAMES, SMILE_RESET, CORNERS_RAISE_THRESHOLD

class MouthDetector:
    def __init__(self, smile_threshold=SMILE_THRESHOLD, min_hold_frames=SMILE_HOLD_FRAMES, reset_threshold=SMILE_RESET, corner_raise_threshold=CORNERS_RAISE_THRESHOLD):
        self.smile_threshold = smile_threshold
        self.min_hold_frames = min_hold_frames
        self.reset_threshold = reset_threshold
        self.corner_raise_threshold = corner_raise_threshold

        # History for stability (to prevent accidental tiny twitches)
        self.smile_history = deque(maxlen=min_hold_frames)

        # The State Lock
        self.active_smile_lock = False  # When True, we are "waiting" for you to stop smiling

        # Landmark indices
        self.LEFT_CORNER = 61
        self.RIGHT_CORNER = 291
        self.UPPER_CENTER = 13
        self.LOWER_CENTER = 14

    def _get_mouth_metrics(self, landmarks):
        """Calculates width/height ratio and corner elevation"""
        left = np.array(landmarks[self.LEFT_CORNER][:2])
        right = np.array(landmarks[self.RIGHT_CORNER][:2])
        upper = np.array(landmarks[self.UPPER_CENTER][:2])
        lower = np.array(landmarks[self.LOWER_CENTER][:2])

        width = np.linalg.norm(right - left)
        height = np.linalg.norm(lower - upper)
        ratio = width / height if height != 0 else 0
        
        # Positive if corners are above the vertical center of the mouth
        center_y = (landmarks[self.UPPER_CENTER][1] + landmarks[self.LOWER_CENTER][1]) / 2
        corners_y = (landmarks[self.LEFT_CORNER][1] + landmarks[self.RIGHT_CORNER][1]) / 2
        raise_amount = center_y - corners_y

        return ratio, raise_amount

    def process(self, landmarks):
        if landmarks is None:
            return {'is_smiling': False, 'smile_triggered': False}

        ratio, corners_raised = self._get_mouth_metrics(landmarks)
        
        # 1. Detection
        is_smiling_now = (ratio > self.smile_threshold) and (corners_raised > self.corner_raise_threshold)
        self.smile_history.append(is_smiling_now)
        confirmed_smile = all(self.smile_history) and len(self.smile_history) == self.min_hold_frames

        smile_triggered = False

        # 2. Logic for One-Shot
        if confirmed_smile:
            if not self.active_smile_lock:
                smile_triggered = True
                self.active_smile_lock = True # Lock is now ON
        
        # 3. THE FIX: Better Reset Logic
        # If your mouth ratio drops below the reset threshold OR 
        # if the landmarks show you are definitely NOT smiling anymore
        if ratio < self.reset_threshold or not is_smiling_now:
            self.active_smile_lock = False # Lock is now OFF

        return {
            "is_smiling": confirmed_smile,
            "smile_triggered": smile_triggered,
            "mouth_ratio": ratio,
            "corners_raised": corners_raised,
            "lock": self.active_smile_lock # Return this so we can see it on screen
        }