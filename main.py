import cv2
import numpy as np
import time 
from utils.config import CAMERA_INDEX
from utils.fps_counter import FPSCounter
from core.webcam import WebCam
from core.face_mesh_engine import FaceMeshEngine
from detectors.eye_detector import EyeDetector
from detectors.head_detector import HeadDetector
from actions.keyboard_actions import KeyboardActions


def main():
    try:
        cam = WebCam(CAMERA_INDEX)
    except RuntimeError as e:
        print(e)
        return
    
    # ────────────── Initialize components ────────────>start
    fps_counter = FPSCounter()
    mesh_engine = FaceMeshEngine()
    eye_detector = EyeDetector()
    head_detector = HeadDetector()
    keyboard_action = KeyboardActions()
    # ────────────── Initialize components ────────────>end

    print("Press 'q' to quit!")

    while True:
        frame = cam.read_frame()
        if frame is None:
            print('Failed to grab frame!')
            break

        frame = cv2.flip(frame, 1)        #Mirror camera for natural view

        # ────── Face Mesh Processing to get landmarks (468 pts. on face) ─────
        results = mesh_engine.process(frame)
        frame = mesh_engine.draw_mesh(frame, results)

        if results.multi_face_landmarks:
            landmarks = mesh_engine.get_landmarks(results)

            # ──────────────────────────────────────────────────────────────── Head pose & movements ────────────────────────────────────────────────────────────>start
            pose = head_detector.update(landmarks)
            current_pitch = pose['pitch']
            current_yaw = pose['yaw']
            current_roll = pose['roll']
            direction = pose['direction']

            # ──────────Action based on the Head turn left or right ─────>start
            turn = head_detector.detect_single_turn(current_yaw)
            if turn == 'right':
                #action if head turns right
                pass
            elif turn == 'left':
                #action if head turns left
                pass
            # ──────────Action based on the Head turn left or right ─────>end

            #show real time direction on camera window
            cv2.putText(frame, f"Head: {direction} ",(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            # Show real time pitch, yaw and roll on camera window for debugging/tuning  
            cv2.putText(frame, f"Pitch: {current_pitch:.2f}  Yaw: {current_yaw:.2f} Roll: {current_roll:.2f}",(10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)


            # ──────────────────────────────────────────────────────────────── Head pose & movements ────────────────────────────────────────────────────────────>end


            # ─────────────────────────────────────────────────────  Eye Wink and EyeBrow Detection  ────────────────────────────────────────────────────────────>start
            # ── Eye detection ──
            eye_states = eye_detector.process(landmarks)

            #show real time EAR for left and right eye for fine tuning and debugging
            cv2.putText(frame, f"L EAR: {eye_states['left_ear']:.2f}  R EAR: {eye_states['right_ear']:.2f}",(10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Eyebrow raise display for fine tuning
            cv2.putText(frame, f"Brow dist: {eye_states['brow_distance']:.3f}",(10, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)

            # ─────────────────────────────Action based on the Eye wink and EyeBrow raise ─────────────────────────────────────>start
            if eye_states["both_blink"]:
                cv2.putText(frame, "NATURAL BLINK (ignored)",(10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                #no action here, its for both eye natural blink, so it's ignored
                pass

            elif eye_states["left_wink"]:
                cv2.putText(frame, "LEFT WINK!",(10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                # Add action here if needed
                pass

            elif eye_states["right_wink"]:
                cv2.putText(frame, "RIGHT WINK!",(10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                # Add action here if needed
                pass

            if eye_states["eyebrow_raised_3sec"]:
                cv2.putText(frame, "EYEBROWS RAISED 3s → ACTION!",(10, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)
                pass

            # One-shot eyebrow trigger (if you added it)
            if eye_states.get("eyebrow_triggered", False):
                cv2.putText(frame, "LOCK TRIGGERED!",(10, 280), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                # kb.lock_windows()  # or your lock function
                pass

            # ─────────────────────────────Action based on the Eye wink and EyeBrow raise ─────────────────────────────────────>start
            # ─────────────────────────────────────────────────────  Eye Wink and EyeBrow Detection  ────────────────────────────────────────────────────────────>end
            
            
            # ─────────────────────────────────────────────────────  Mouth Detection and Action Logic  ────────────────────────────────────────────────────────────>start
            mouth_states = mouth_detector.process(landmarks)

            #for debugging and fine tuning smiling 
            cv2.putText(frame, f"Mouth Ratio: {mouth_states['mouth_ratio']:.2f}", (10, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 255), 2)

            cv2.putText(frame, f"Corner Raised: {mouth_states['corners_raised']:.4f}", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 255), 2)

            # One-shot Action to be performed on smiling
            if mouth_states['smile_triggered']:
                cv2.putText(frame, f"SMILE DETECTED", (10, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                print('Smile Detected')
                # kb.copy()

            # The VISUAL (Stays on screen while you are smiling)
            if mouth_states['is_smiling']:
                cv2.putText(frame, "SMILING", (10, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
            
            # ─────────────────────────────────────────────────────  Mouth Detection and Action Logic  ────────────────────────────────────────────────────────────>end
            

        # ── Display FPS on cam window ──
        cv2.putText(frame, fps_counter.get_text(),(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the camera window
        cv2.imshow("Iris-OS - Webcam", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cam.release()
    cv2.destroyAllWindows()
    print("Webcam closed cleanly.")

if __name__ == "__main__":
    main()