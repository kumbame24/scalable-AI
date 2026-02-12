import time

def normalize(event, source="video", session_id=1):
    return {
        "source": source,
        "session_id": session_id,
        "sensor_id": 1,
        "event_type": event["type"],
        "confidence": event["confidence"],
        "timestamp": time.time()
    }
