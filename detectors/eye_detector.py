import numpy as np
from collections import deque
from utils.config import EYE_CONFIG, BROW_CONFIG

class EyeDetector:
    def __init__(self, fps=30):
        self.left_ear_threshold = EYE_CONFIG['LEFT_THRESHOLD']
        self.right_ear_threshold = EYE_CONFIG['RIGHT_THRESHOLD']
        self.ear_consec_frames = EYE_CONFIG['CONSEC_FRAMES']
        self.fps = fps

        #for left and right eye separately
        self.left_ear_history = deque(maxlen=self.ear_consec_frames)
        self.right_ear_history = deque(maxlen=self.ear_consec_frames)

        #landmark indices (MediaPipe Face Mesh Standard)
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]

        # Eyebrow landmarks (middle points for average)
        self.LEFT_BROW = [70, 63, 105]
        self.RIGHT_BROW = [300, 293, 334]
        self.LEFT_EYE_TOP = [159, 145]
        self.RIGHT_EYE_TOP = [386, 374]

        #for holding raised eyebrows
        self.raised_count = 0
        self.raised_threshold_frames = BROW_CONFIG['HOLD_FRAMES']
        self.brow_raise_threshod = BROW_CONFIG['RAISE_THRESHOLD']

    def _eye_aspect_ratio(self, eye_points):
        """calculate EAR for one eye (6 pts.)"""
        p1, p2, p3, p4, p5, p6 = eye_points
        vertical1 = np.linalg.norm(p2 - p6)
        vertical2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)

        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear
    
    def _get_eyebrow_distance(self, landmarks):
        """returns average normalized vertical distance between eye and brow"""
        if landmarks is None:
            return 0.0
        
        #left side
        left_brow_y = np.mean([landmarks[i][1] for i in self.LEFT_BROW])
        left_eye_y = np.mean([landmarks[i][1] for i in self.LEFT_EYE_TOP])

        #right side
        right_brow_y = np.mean([landmarks[i][1] for i in self.RIGHT_BROW])
        right_eye_y = np.mean([landmarks[i][1] for i in self.RIGHT_EYE_TOP])

        #average distance (larger = raiser)
        dist_left = left_eye_y - left_brow_y
        dist_right = right_eye_y - right_brow_y

        return (dist_left + dist_right) / 2
    
    def process(self, landmarks):
        """landmarks: list of 468 pts [x, y, z] (normalized).    Returns dict with blink/wink states"""
        if landmarks is None or len(landmarks) < 468:
            return {
                "left_wink": False,
                "right_wink": False,
                "both_blink": False,
                "left_closed": False,
                "right_closed": False,
                "left_ear": 0.3,
                "right_ear": 0.3
            }
        
        #extract eye points
        left_eye_pts = [np.array(landmarks[i][:2]) for i in self.LEFT_EYE]
        right_eye_pts = [np.array(landmarks[i][:2]) for i in self.RIGHT_EYE]

        left_ear = self._eye_aspect_ratio(left_eye_pts)
        right_ear = self._eye_aspect_ratio(right_eye_pts)

        #store in history
        self.left_ear_history.append(left_ear)
        self.right_ear_history.append(right_ear)

        #blink in EAR < ear_threshold for enough consecutive frames
        left_closed = all(e < self.left_ear_threshold for e in self.left_ear_history)
        right_closed = all(e < self.right_ear_threshold for e in self.right_ear_history)

        both_blink = left_closed and right_closed
        #key logic:  wink = one eye clearly closed and another eye cleared open
        left_wink = left_closed and (right_ear > self.left_ear_threshold * 1.3)
        right_wink = right_closed and (left_ear > self.right_ear_threshold * 1.3)

        # ────────────────────────── EyeBrow Raise detection logic ────────────────> start
        brow_dist = self._get_eyebrow_distance(landmarks)
        is_raised = brow_dist > self.brow_raise_threshod

        eyebrow_held = False
        eyebrow_triggered = False

        if is_raised:                     #testing printing on terminal , for how many is eyebrows up
            print(f"Raised! dist={brow_dist:.4f}  count={self.raised_count}/{self.raised_threshold_frames}")
           
        if is_raised:
            self.raised_count += 1
            if self.raised_count >= self.raised_threshold_frames:
                eyebrow_held = True
                #logic below lets only perform the action once set to picking up eyebrows 3 sec     -> start
                # If we haven't triggered yet in this hold → fire action
                if not hasattr(self, 'already_triggered') or not self.already_triggered:
                    eyebrow_triggered = True # Matches initialization now
                    self.already_triggered = True# Block further triggers
                    #trigger action only once eyebrows picking up 3sec            -> end
            else:
                eyebrow_held = False
        else:
            self.raised_count = 0
            eyebrow_held = False
            self.already_triggered = False  # Allow next raise to trigger again
        #Eyebrow raise detection logic starts here              -> start



        return {
            "left_wink": left_wink,
            "right_wink": right_wink,
            "both_blink": both_blink,
            "left_closed": left_closed,
            "right_closed": right_closed,
            "eyebrow_raised_3sec": eyebrow_held,
            "eyebrow_triggered": eyebrow_triggered,       # True only once per hold
            "left_ear": left_ear,
            "right_ear": right_ear,
            "brow_distance": brow_dist
        }

