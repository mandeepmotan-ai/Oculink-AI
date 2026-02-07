import cv2

class WebCam:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam. Check if another app is using it.")
        
        #get camera resolution
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f'WebCam Opened: {self.width} * {self.height}')


    def read_frame(self):
        #returns one frame (BGR image) or None if failed
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame
    
    def release(self):
        self.cap.release()