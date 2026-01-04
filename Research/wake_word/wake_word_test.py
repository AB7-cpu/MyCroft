import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np

# Load your custom model
model = Model(wakeword_models=["hey_mycroft"])

# Audio stream setup (Standard PyAudio)
audio = pyaudio.PyAudio()
mic = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)

print("Listening for 'Victus'...")
i = 0
while True:
    # Get audio
    audio_data = np.frombuffer(mic.read(1280), dtype=np.int16)
    
    # Feed to model
    prediction = model.predict(audio_data)
    
    # Check score (0.0 to 1.0)
    if prediction["hey_mycroft"] > 0.5:
        print(f"{i}: Wake word detected!")
        i += 1
        # Trigger your VAD + Whisper pipeline here