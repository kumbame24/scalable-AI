def detect(energy, threshold=0.01):
    if energy > threshold:
        return {
            "type": "AUDIO_ANOMALY",
            "confidence": 0.6
        }
    return None
