import webrtcvad
import pyaudio

vad = webrtcvad.Vad(2)
audio = pyaudio.PyAudio()

stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=320)

print("Listening...")

while True:
    frame = stream.read(320)
    if vad.is_speech(frame, 16000):
        print("Speech detected")
