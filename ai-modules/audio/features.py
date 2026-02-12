import librosa
import numpy as np

def extract(audio, fs=16000):
    mfcc = librosa.feature.mfcc(y=audio, sr=fs, n_mfcc=13)
    energy = np.sum(audio ** 2)
    zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
    return mfcc.mean(axis=1), energy, zcr
