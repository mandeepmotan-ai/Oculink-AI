import cv2
import mediapipe as mp

class FaceMeshEngine:
    """
    MediaPipe Face Mesh - 468 landmarks with iris refinement. 
    used for detailed face analysis (head pose, mouth, eye)
    """
    def __init__(self, 
                 max_faces=1,
                 refine_landmarks=True,
                 min_detection_conf=0.7,
                 min_tracking_conf=0.7):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_model=False,
            max_num_faces=max_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_conf,
            min_tracking_confidence=min_tracking_conf
        )

        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1)

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results=self.face_mesh.process(rgb)
        return results
    
    def draw_mesh(self, frame, results):
        """draw the full face mesh (tesselation + contours)"""
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                self.mp_draw.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.drawing_spec
                )
                #draw iris
                self.mp_draw.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_IRISES,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_draw.DrawingSpec(color=(0,0,255), thickness=1)
                )
        return frame 
    
    def get_landmarks(self, results):
        """returns a list of (x,y,z) for all 468 pts. normalized (0-1)"""
        if results.multi_face_landmarks:
            return [[lm.x, lm.y, lm.z] for lm in results.multi_face_landmarks[0].landmark]