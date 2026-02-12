import cv2
import threading
import requests
import time
import logging
from camera import Camera
from objects import ObjectDetector
from gaze import GazeDetector
from events import normalize
import server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000/events"

def run_vision_loop():
    cam = None
    obj = ObjectDetector()
    gaze = GazeDetector()
    
    # Fetch active session ID
    session_id = 1
    try:
        resp = requests.get("http://localhost:8000/examinations/active", timeout=2)
        if resp.ok and resp.json():
            session_id = resp.json().get("id", 1)
            logger.info(f"Connected to active examination session: {session_id}")
    except Exception as e:
        logger.warning(f"Could not fetch active examination, using default ID 1: {e}")

    logger.info("Vision Module Started")
    logger.info(f"Camera active status: {server.camera_active}")

    while True:
        if not server.camera_active:
            if cam is not None:
                cam.release()
                cam = None
                logger.info("Camera stopped by user")
            time.sleep(0.5)
            continue
            
        if cam is None:
            logger.info("Initializing camera...")
            try:
                cam = Camera()
                logger.info("Camera initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize camera: {e}")
                time.sleep(2)
                continue
            
        frame = cam.read()
        if frame is None:
            logger.warning("Failed to read frame from camera")
            time.sleep(0.1)
            continue

        # detection
        detected_objects = obj.detect(frame)
        gaze_result = gaze.detect(frame)

        # Drawing and sending events
        for e in detected_objects:
            try:
                requests.post(BACKEND_URL, json=normalize(e, session_id=session_id), timeout=1)
                if server.captions_active:
                    cv2.putText(frame, f"{e['object']} ({e['confidence']:.2f})", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            except Exception as ex:
                logger.error(f"Error sending object event: {ex}")

        if gaze_result:
            try:
                requests.post(BACKEND_URL, json=normalize(gaze_result, session_id=session_id), timeout=1)
                if server.captions_active:
                    cv2.putText(frame, f"GAZE: {gaze_result['direction']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            except Exception as ex:
                logger.error(f"Error sending gaze event: {ex}")

        # Update streaming frame
        with server.lock:
            server.output_frame = frame.copy()
        
        # throttle to save CPU
        time.sleep(0.03)

    if cam:
        cam.release()

if __name__ == "__main__":
    logger.info("Starting vision server...")
    t = threading.Thread(target=run_vision_loop, daemon=True)
    t.start()
    
    server.start_server()
