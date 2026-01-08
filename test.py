# listener.py
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import io
import wave

# Load model once
model = WhisperModel('medium', device="cuda", compute_type="float16")

def record_audio(duration=5, samplerate=16000):
    print("🎙️ Listening...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    return audio, samplerate

def take_command(duration=5):
    audio, samplerate = record_audio(duration)

    # Convert NumPy array to bytes in memory (no saving)
    byte_io = io.BytesIO()
    with wave.open(byte_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16 → 2 bytes
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())

    byte_io.seek(0)

    # Transcribe directly from memory
    segments, _ = model.transcribe(byte_io)
    text = " ".join(segment.text for segment in segments).strip().lower()
    print(f"✅ Heard: {text}")
    return text


take_command()

