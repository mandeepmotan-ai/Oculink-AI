import time 

class FPSCounter:
    def __init__(self):
        self.prev_time = time.time()
        self.fps = 0.0
    
    def update(self):
        current_time = time.time()
        dt = current_time - self.prev_time
        if dt > 0:
            self.fps = 1/dt
        self.prev_time = current_time
        return self.fps
    
    def get_text(self, decimals=1):
        return f"FPS : {self.fps:.{decimals}f}"