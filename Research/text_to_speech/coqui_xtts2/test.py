import asyncio
import re
import sounddevice as sd
import torch
from TTS.api import TTS
import numpy as np

SAMPLE_RATE = 24000
VOICE = "Luis Moray"

def split_sentences(text):
    return re.split(r'(?<=[.!?…])\s+', text)

def add_preroll(wav, sr=24000, ms=80):
    wav = np.asarray(wav, dtype=np.float32)   # 🔥 FIX
    silence = np.zeros(int(sr * ms / 1000), dtype=wav.dtype)
    return np.concatenate([silence, wav])

async def tts_producer(sentences, audio_queue, tts):
    for sentence in sentences:
        if not sentence.strip():
            continue

        # Generate audio (GPU-bound)
        wav = await asyncio.to_thread(
            tts.tts,
            text=sentence,
            speaker=VOICE,
            language="en"
        )

        wav = add_preroll(wav)
        await audio_queue.put(wav)

    await audio_queue.put(None)  # signal end

async def audio_consumer(audio_queue):
    while True:
        wav = await audio_queue.get()

        if wav is None:
            # Only exit AFTER queue is empty
            if audio_queue.empty():
                break
            else:
                continue

        sd.play(wav, SAMPLE_RATE)
        await asyncio.to_thread(sd.wait)


async def main(llm_output):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    sentences = split_sentences(llm_output)
    audio_queue = asyncio.Queue(maxsize=5)  # small buffer = low latency

    await asyncio.gather(
        tts_producer(sentences, audio_queue, tts),
        audio_consumer(audio_queue),
    )

# ---------- TEST ----------
llm_output = """
Alright. I’m ready.

I’ve checked everything you asked for, and the setup looks solid so far.
Now — this should feel faster… and more natural.

Tell me — does this feel responsive?
"""

asyncio.run(main(llm_output))
