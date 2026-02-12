import requests
from capture import record
from features import extract
from anomaly import detect
from time import sleep, time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000/events"

def run_audio_loop():
    logger.info("Audio Module Started")
    
    # Fetch active session ID
    session_id = 1
    try:
        resp = requests.get("http://localhost:8000/examinations/active", timeout=2)
        if resp.ok and resp.json():
            session_id = resp.json().get("id", 1)
            logger.info(f"Connected to active examination session: {session_id}")
    except Exception as e:
        logger.warning(f"Could not fetch active examination, using default ID 1: {e}")
    
    while True:
        try:
            audio = record()
            _, energy, _ = extract(audio)
            event = detect(energy)
            if event:
                event_data = {
                    "source": "audio",
                    "session_id": session_id,
                    "sensor_id": 2,
                    "event_type": event["type"],
                    "confidence": event["confidence"],
                    "timestamp": time()
                }
                try:
                    response = requests.post(BACKEND_URL, json=event_data, timeout=5)
                    response.raise_for_status()
                    logger.debug(f"Event posted: {event['type']} ({event['confidence']:.2f})")
                except requests.RequestException as e:
                    logger.error(f"Failed to post event: {e}")
            sleep(1)
        except Exception as e:
            logger.error(f"Error in audio loop: {e}")
            sleep(1)

if __name__ == "__main__":
    run_audio_loop()
