from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import threading
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global flag to control camera
camera_active = True
output_frame = None
lock = threading.Lock()

def generate():
    global output_frame, lock, camera_active
    while True:
        if not camera_active:
            # Yield a placeholder frame or just silence?
            # For MJPEG, it's better to verify connection is kept open or yield a static "OFF" frame.
            # For simplicity, we'll just yield nothing and sleep, relying on frontend to handle the visual.
            # OR we can generate a black frame.
            time.sleep(0.5)
            continue

        with lock:
            if output_frame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)
            if not flag:
                continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
               bytearray(encodedImage) + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/camera/start")
def start_camera():
    global camera_active
    camera_active = True
    return {"status": "started"}

@app.post("/camera/stop")
def stop_camera():
    global camera_active
    camera_active = False
    return {"status": "stopped"}

@app.get("/status")
def status():
    return {"status": "running", "camera_active": camera_active, "captions_active": captions_active}

# Global flag to control captions
captions_active = True

@app.post("/captions/start")
def start_captions():
    global captions_active
    captions_active = True
    return {"status": "captions_enabled"}

@app.post("/captions/stop")
def stop_captions():
    global captions_active
    captions_active = False
    return {"status": "captions_disabled"}

def start_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")
