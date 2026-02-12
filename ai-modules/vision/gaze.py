import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python.vision import face_landmarker
import urllib.request
import os
import logging

logger = logging.getLogger(__name__)

class GazeDetector:
    def __init__(self):
        try:
            # Download the face landmarker model if not present
            model_path = "face_landmarker.task"
            if not os.path.exists(model_path):
                logger.info("Downloading face landmarker model...")
                model_url = "https://storage.googleapis.com/mediapipe-models/vision/face_landmarker/float16/1/face_landmarker.task"
                try:
                    urllib.request.urlretrieve(model_url, model_path)
                    logger.info(f"Model downloaded to {model_path}")
                except Exception as e:
                    logger.warning(f"Could not download model: {e}")
                    logger.warning("Gaze detection will be disabled")
                    self.face_landmarker = None
                    return
            
            # Use the downloaded model
            base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
            options = face_landmarker.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=False,
                output_facial_transformation_matrixes=False,
                num_faces=1
            )
            self.face_landmarker = face_landmarker.FaceLandmarker.create_from_options(options)
            logger.info("Gaze detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize gaze detector: {e}")
            self.face_landmarker = None

    def detect(self, frame):
        if self.face_landmarker is None:
            # Fallback: no detection available
            return None
            
        # Convert frame to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # Detect face landmarks
        detection_result = self.face_landmarker.detect(mp_image)
        
        if not detection_result.face_landmarks or len(detection_result.face_landmarks) == 0:
            return None

        # Convert landmarks to image coordinates
        landmarks = detection_result.face_landmarks[0]
        mesh_points = np.array([[int(p.x * frame.shape[1]), int(p.y * frame.shape[0])] for p in landmarks])
        
        # Iris indices
        # Left iris: 474-477, Right iris: 469-472
        # Center of eyes (approx)
        left_iris = mesh_points[468]
        right_iris = mesh_points[473]
        
        # Eye corners for reference
        # Left eye: 33 (inner), 133 (outer)
        # Right eye: 362 (inner), 263 (outer)
        
        # Simple Logic: Check relative position of iris within eye
        # For this demo, we'll return a basic "Looking Away" if head pose is extreme or iris is off-center
        
        # Placeholder for complex vector math - using head pose approximation
        # Nose tip: 1
        nose_tip = mesh_points[1]
        left_cheek = mesh_points[234]
        right_cheek = mesh_points[454]
        
        # Calculate horizontal balance
        face_width = right_cheek[0] - left_cheek[0]
        nose_offset = nose_tip[0] - left_cheek[0]
        ratio = nose_offset / face_width
        
        direction = "CENTER"
        if ratio < 0.4:
            direction = "LOOKING LEFT"
        elif ratio > 0.6:
            direction = "LOOKING RIGHT"
            
        if direction != "CENTER":
            return {
                "type": "GAZE_DEVIATION",
                "direction": direction,
                "confidence": 0.85
            }
        return None
