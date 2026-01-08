
import asyncio
import websockets
import numpy as np
import sounddevice as sd
from urllib.parse import urlencode
from collections import deque

# Constants
SAMPLE_RATE = 24000
CHANNELS = 1
DTYPE = "float32"

# Global buffer for the callback
audio_buffer = deque()
_stream = None

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

def start_stream():
    """Starts a persistent audio stream."""
    global _stream
    if _stream is None:
        _stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=audio_callback,
            blocksize=512,
        )
        _stream.start()
        print("🔈 Audio stream started")

def stop_stream():
    """Stops the persistent audio stream."""
    global _stream
    if _stream is not None:
        _stream.stop()
        _stream.close()
        _stream = None
        audio_buffer.clear()
        print("🔇 Audio stream stopped")

async def wait_until_done():
    """Waits until the audio buffer is completely empty and played."""
    while audio_buffer:
        await asyncio.sleep(0.05)
    # Small extra wait to ensure the last burst is physically played by hardware
    await asyncio.sleep(0.2)

async def ws_receiver(text, voice):
    params = {
        "text": text,
        "voice": voice,
        "cfg": 1.5,
        "steps": 5,
    }
    WS_URL = f"ws://localhost:3000/stream?{urlencode(params)}"

    try:
        async with websockets.connect(WS_URL, max_size=None) as ws:
            async for msg in ws:
                if isinstance(msg, bytes):
                    # PCM16 → float32
                    samples = (
                        np.frombuffer(msg, dtype=np.int16)
                        .astype(np.float32) / 32768.0
                    )
                    audio_buffer.append(samples)
    except Exception as e:
        print(f"WebSocket Error: {e}")


async def speak_async(text: str, voice: str = 'en-Mike_man'):
    """
    Asynchronous version of speak.
    Appends to the global buffer while the persistent stream plays it.
    """
    if not text.strip():
        return
    
    # Ensure stream is running
    if _stream is None:
        start_stream()
        
    await ws_receiver(text, voice)


def speak(text: str, voice: str = 'en-Mike_man'):
    """
    Synchronous wrapper for VibeVoice TTS.
    """
    if not text.strip():
        return
        
    try:
        # For synchronous usage, we start/stop manually
        start_stream()
        asyncio.run(speak_async(text, voice))
        asyncio.run(wait_until_done())
        stop_stream()
    except Exception as e:
        print(f"TTS Error: {e}")


if __name__ == "__main__":
    TEXT = """
    Alright, let’s take a moment and slow things down.

This is a full voice quality test — not just to hear how clear the voice sounds,
but to understand how natural it feels over time.

First, listen to the pauses.
Notice how the voice stops…
and then continues — without sounding robotic or rushed.

Now let’s try something conversational.

Imagine you’re sitting at your desk late at night.
The room is quiet, the screen is glowing softly,
and you ask your assistant a simple question —
“Hey, are you still there?”

The reply shouldn’t feel mechanical.
It should feel present.
Calm.
Almost human.

Let’s add some numbers.

Today is September 18th, 2025.
The time is 11:47 p.m.
Your battery is at 23 percent,
and you have exactly three notifications waiting.

Now here’s a longer sentence — listen carefully.

Even though modern artificial intelligence systems are incredibly fast,
what truly matters is not how quickly they respond,
but how comfortably humans can interact with them
over long periods of time.

Short sentence.

Long sentence again — with commas, pauses, and emphasis.

When an assistant speaks, it shouldn’t sound like it’s reading text aloud;
instead, it should sound like it’s thinking while speaking,
adjusting its tone naturally as the conversation unfolds.

Let’s test questions.

Does this sound responsive?
Does it feel smooth?
Would you be comfortable listening to this voice
for several minutes at a time?

Now, let’s test emotion — very subtle emotion.

I’m glad you’re here.

Not excited.
Not flat.
Just… calm and reassuring.

Finally, we’ll end with something reflective.

Technology should never feel cold or distant.
When it works well, it fades into the background
and simply feels like a helpful presence —
quietly waiting until you need it.

Alright.
That concludes this voice test.
Take a moment, listen back,
and trust your instincts.
"""
    print(f"Speaking: {TEXT}")
    speak(TEXT)
