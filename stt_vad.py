import webrtcvad
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import collections
import io
import wave
import sys
import time

# Constants
RATE = 16000
FRAME_DURATION_MS = 30
CHUNK_SIZE = int(RATE * FRAME_DURATION_MS / 1000)  # 480 samples
VAD_MODE = 3  # Aggressiveness: 0-3
SILENCE_DURATION_S = 1.0  # Stop generally after 1.0s of silence
PRE_BUFFER_DURATION_S = 0.5 # Keep 0.5s before speech

# Global Model Loading (Lazy loaded or on import)
# Using 'cuda' and 'float16' as per user's test.py
print("⏳ Loading Whisper Model...")
model = WhisperModel('medium', device="cuda", compute_type="float16")
print("✅ Whisper Model Loaded")

vad = webrtcvad.Vad(VAD_MODE)

def is_speech(frame, sample_rate):
    """Returns True if the frame contains speech."""
    try:
        return vad.is_speech(frame, sample_rate)
    except:
        return False

def take_command(timeout=None):
    """
    Listens continuously until speech is detected, then records until silence.
    Returns the transcribed text.
    Args:
        timeout: Max seconds to wait for speech start. If None, waits indefinitely.
    """
    
    # Ring buffer for pre-roll
    num_padding_chunks = int(PRE_BUFFER_DURATION_S / (FRAME_DURATION_MS / 1000))
    ring_buffer = collections.deque(maxlen=num_padding_chunks)
    
    triggered = False
    voiced_frames = []
    
    # Counter for silence duration
    silence_chunks = 0
    max_silence_chunks = int(SILENCE_DURATION_S / (FRAME_DURATION_MS / 1000))
    
    # Timeout tracking
    start_time = time.time() if timeout else None
    
    print(f"🎙️ Listening (VAD, timeout={timeout}s)...")
    
    # Using a stream for low latency
    with sd.InputStream(samplerate=RATE, channels=1, dtype='int16', blocksize=CHUNK_SIZE) as stream:
        while True:
            chunk, overflowed = stream.read(CHUNK_SIZE)
            if overflowed:
                pass
                
            # timeout check (only if not yet triggered)
            if timeout and not triggered:
                if (time.time() - start_time) > timeout:
                    return None

            # Convert to bytes for VAD
            chunk_bytes = chunk.tobytes()
            
            # Helper to check speech
            active = is_speech(chunk_bytes, RATE)
            
            if not triggered:
                ring_buffer.append(chunk_bytes)
                if active:
                    print("🗣️ Speech started...")
                    triggered = True
                    voiced_frames.extend(ring_buffer) # Add pre-roll
                    voiced_frames.append(chunk_bytes)
                    silence_chunks = 0
            else:
                voiced_frames.append(chunk_bytes)
                if active:
                    silence_chunks = 0
                else:
                    silence_chunks += 1
                
                # Check if silence exceeded limit
                if silence_chunks > max_silence_chunks:
                    print("🤫 Silence detected, processing...")
                    triggered = False
                    break

    # Process audio
    if not voiced_frames:
        return None

    # Stitch frames
    audio_data = b''.join(voiced_frames)
    
    # Create wav in memory
    byte_io = io.BytesIO()
    with wave.open(byte_io, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(audio_data)
    
    byte_io.seek(0)
    
    # Transcribe
    try:
        segments, _ = model.transcribe(byte_io)
        text = " ".join(segment.text for segment in segments).strip()
        if text:
            print(f"✅ Heard: {text}")
            return text
        else:
            return None
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

if __name__ == "__main__":
    while True:
        res = take_command()
        if res:
            print(f"Result: {res}")
