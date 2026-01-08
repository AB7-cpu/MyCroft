import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np
import logging

# Suppress warnings
logging.getLogger('openwakeword').setLevel(logging.ERROR)

# Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280
THRESHOLD = 0.5

print("⏳ Loading Wake Word Model...")
# Load the model (downloads automatically if not present)
model = Model(wakeword_models=["hey_mycroft"], inference_framework="onnx")
print("✅ Wake Word Model Loaded")

def listen_for_wake_word():
    """
    Listens continuously for the wake word 'Hey Mycroft'.
    Blocking call. Returns True when detected.
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    # print("\n💤 Waiting for wake word ('Hey Mycroft')...")
    
    try:
        while True:
            # Read audio chunk
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Feed to model
            prediction = model.predict(audio_data)
            
            # Check for wake word
            if prediction["hey_mycroft"] > THRESHOLD:
                # print("⚡ Wake Word Detected!")
                return True
                
    except KeyboardInterrupt:
        return False
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        # Reset model buffer to avoid false triggers on next run
        model.reset()

if __name__ == "__main__":
    while True:
        if listen_for_wake_word():
            print("Wake word detected!")
