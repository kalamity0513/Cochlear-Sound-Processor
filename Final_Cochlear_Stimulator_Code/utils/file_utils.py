from PIL import Image, ImageTk
import sounddevice as sd
import numpy as np
import os

def load_icon(path, size=(128, 128)):
    try:
        img = Image.open(path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except:
        print(f"Missing icon: {path}")
        return None

def play_click(sound):
    try:
        sound.play()
    except:
        pass

def play_wav(wav_path):
    if wav_path and os.path.exists(wav_path):
        import soundfile as sf
        x, fs = sf.read(wav_path)
        if x.ndim > 1:
            x = x[:, 0]
        sd.stop()
        sd.play(x, fs)
