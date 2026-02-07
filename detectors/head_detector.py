import numpy as np
import time
from utils.config import YAW_THRESHOLD

class HeadDetector:
    def __init__(self, yaw_threshold=YAW_THRESHOLD, fps=30):
        # ── Thresholds ──
        self.yaw_threshold = yaw_threshold
        self.return_threshold = yaw_threshold * 0.7
        
        # ── State Tracking (Memory) ──
        self.head_state = "center"
        self.last_action_time = 0.0
        self.cooldown = 0.5                   #seconds between allowed triggers to avoid spam

    def update(self, landmarks):
        """Calculates the real time yaw, pitch, roll. Call this every frame"""
        if landmarks is None or len(landmarks) < 468:
            return {'yaw':0.0, 'pitch':0.0, 'roll':0.0, 'direction':'center'}

        # ────────────────────────── Landmark Math ────────────────> start
        nose = np.array(landmarks[11])
        left_ear = np.array(landmarks[234])
        right_ear = np.array(landmarks[454])
        chin = np.array(landmarks[152])
        forehead = np.array(landmarks[10])
        left_eye_outer = np.array(landmarks[33])
        right_eye_outer = np.array(landmarks[263])
        
        # Yaw: nose horizontal relative to ears
        ear_center_x = (left_ear[0] + right_ear[0]) / 2
        yaw = (nose[0] - ear_center_x) * 5.0

        # Pitch: nose vertical relative to forehead/chin
        vertical_center = (forehead[1] + chin[1]) / 2
        pitch = (nose[1] - vertical_center) * 5.0

        # Roll: eye line angle
        roll = np.arctan2(right_eye_outer[1] - left_eye_outer[1],
                          right_eye_outer[0] - left_eye_outer[0]) * (180/np.pi)

        # ────────────────────────── Landmark Math ────────────────> end

        direction = 'center'
        if yaw>self.yaw_threshold:
            direction='right'
        elif yaw<-self.yaw_threshold:
            direction='left'
        
        return {'yaw':yaw, 'pitch':pitch, 'roll':roll, 'direction':direction}

    def detect_single_turn(self, current_yaw):
        """
        Logic : Trigger once when crossing threshold 
        Reset only when returning to center
        """
        action = None
        now = time.time()

        # ─────────────────────── Edge Detection Logic ──────────────> start
        #1. Check if we are currently in "center" and just turned
        if self.head_state == 'center':
            if current_yaw < -self.yaw_threshold:
                if now - self.last_action_time > self.cooldown:
                    action = 'left'
                    self.head_state = 'left'
                    self.last_action_time = now
            elif current_yaw > self.yaw_threshold:
                if now - self.last_action_time > self.cooldown:
                    action = 'right'
                    self.head_state = 'right'
                    self.last_action_time = now
        #2. check if we have returned to center to reset the state
        else :
            #if we are left or right, we must come back towards 0 to allow another trigger (means head comes back at center)
            if abs(current_yaw) < self.return_threshold:
                self.head_state = 'center'
        # ─────────────────────── Edge Detection Logic ──────────────> end
        
        return action 