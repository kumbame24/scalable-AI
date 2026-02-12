import sounddevice as sd
import numpy as np

def record(duration=1, fs=16000):
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten()
