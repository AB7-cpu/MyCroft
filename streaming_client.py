import asyncio
import websockets
import numpy as np
import sounddevice as sd
from urllib.parse import urlencode
from collections import deque

SAMPLE_RATE = 24000
CHANNELS = 1
DTYPE = "float32"

# --- text to speak ---
TEXT = (
    "Alright. "
    "This should start speaking almost immediately. "
    "Does this feel responsive?"
)

params = {
    "text": TEXT,
    "voice": "en-Mike_man",
    "cfg": 1.5,
    "steps": 5,
}

WS_URL = f"ws://localhost:3000/stream?{urlencode(params)}"

# --- continuous sample buffer ---
audio_buffer = deque()
buffer_lock = asyncio.Lock()
stream_finished = False


def audio_callback(outdata, frames, time, status):
    if status:
        print("Audio status:", status)

    samples_needed = frames
    outdata.fill(0)

    while samples_needed > 0 and audio_buffer:
        chunk = audio_buffer[0]

        take = min(len(chunk), samples_needed)
        outdata[frames - samples_needed : frames - samples_needed + take, 0] = chunk[:take]

        if take < len(chunk):
            audio_buffer[0] = chunk[take:]
        else:
            audio_buffer.popleft()

        samples_needed -= take


async def ws_receiver():
    global stream_finished

    async with websockets.connect(WS_URL, max_size=None) as ws:
        print("✅ Connected to VibeVoice WebSocket")

        async for msg in ws:
            if isinstance(msg, bytes):
                # PCM16 → float32
                samples = (
                    np.frombuffer(msg, dtype=np.int16)
                    .astype(np.float32) / 32768.0
                )
                audio_buffer.append(samples)

        print("🔚 WebSocket closed")
        stream_finished = True


async def main():
    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        callback=audio_callback,
        blocksize=512,   # stable
    ):
        await ws_receiver()

        # Wait until buffer fully drains
        while audio_buffer:
            await asyncio.sleep(0.05)


asyncio.run(main())