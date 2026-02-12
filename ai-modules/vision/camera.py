import cv2
import logging

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, source=0):
        logger.info(f"Initializing camera with source: {source}")
        self.cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)  # Use DirectShow on Windows for better compatibility
        
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera source {source}")
            # Try alternative backend
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                logger.error("Failed to open camera with alternative backend")
        else:
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            logger.info("Camera initialized successfully")

    def read(self):
        if not self.cap.isOpened():
            logger.warning("Camera is not opened")
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            return None
        return frame

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
            logger.info("Camera released")
