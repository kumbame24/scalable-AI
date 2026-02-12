from ultralytics import YOLO

class ObjectDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.suspicious = {"cell phone", "book"}

    def detect(self, frame):
        results = self.model(frame, verbose=False)
        events = []

        for r in results:
            for box in r.boxes:
                label = r.names[int(box.cls)]
                if label in self.suspicious:
                    events.append({
                        "type": "OBJECT_DETECTED",
                        "object": label,
                        "confidence": float(box.conf)
                    })
        return events
