# Developer Guide - MyCroft

This guide is for developers (and my future self) to understand the inner workings, architectural decisions, and evolution of the code.

## 🏗️ Architecture

### High-Level Flow (Async Streaming)
1.  **Input (Audio)**: User speaks -> `stt_vad.py` detects voice (VAD) -> Transcribes (Whisper).
2.  **State Machine**: `backup_model.py` manages the Wake Word -> Active -> Sleep states.
3.  **Processing (Agent)**: Text -> `agent.astream()` (LangGraph).
4.  **Real-Time Output**:
    -   Tokens are buffered into **sentences**.
    -   Sentences are put into an `asyncio.Queue`.
    -   **TTS Consumer** (`tts_consumer`) takes sentences from the queue and sends them to VibeVoice.
    -   **VibeVoice Client** (`tts.py`) connects via WebSocket and streams audio chunks into a `deque`.
    -   **Audio Callback**: `sounddevice` pulls from the `deque` for gapless playback.

### Component Deep Dive

#### 1. Speech-to-Text (`stt_vad.py`)
-   **Logic**: Uses a ring buffer and `webrtcvad` to monitor energy. 
-   **Whisper**: Uses `faster_whisper` for local, fast transcription.
-   **Blocking Thread**: Since STT is currently synchronous/cpu-bound, it is run via `asyncio.to_thread` in the main loop to prevent blocking the event loop.

#### 2. The Agent (`backup_model.py`)
-   **Framework**: `langgraph.prebuilt.create_react_agent`.
-   **Streaming**: Shifted from `invoke()` to `astream(stream_mode="messages")`.
-   **Sentence Splitting**: Uses a robust regex `r'(?<=[^0-9][.!?\n])\s+'` to split text without breaking decimals or abbreviations.
-   **Markdown Stripping**: `clean_text_for_tts` removes code blocks, italics, and bold tags before speech generation.

#### 3. Persistent TTS (`tts.py`)
-   **Why Change?**: Shifted from PlayAI (Cloud) -> VibeVoice (Local).
-   **Persistence**: Added `start_stream()` to keep the audio device open. This eliminates the "click" and lag of opening hardware for every sentence.
-   **Buffering**: Uses a `collections.deque` for thread-safe audio chunk storage.

## 📜 History & Evolution

### Phase 1: Basic Scripts (`main.py`)
-   Used `speech_recognition` with fixed timeouts.

### Phase 2: Agentic Workflow (`backup_model.py`)
-   Introduced **LangGraph** and Ollama fallback.

### Phase 3: Advanced Audio & Streaming (Current)
-   **VibeVoice Migration**: Replaced cloud TTS with a local solution.
-   **Async Refactor**: Moved the entire main loop to `asyncio` to allow concurrent thinking and speaking.
-   **TTFW Optimization**: Time To First Word reduced to almost zero by speaking sentences as they are born.

## 📝 Troubleshooting
-   **Choppy Audio**: Ensure the VibeVoice server (`vibevoice_realtime_demo.py`) is running. Check if `blocksize` in `tts.py` needs adjustment for your hardware.
-   **MyCroft Hears Himself**: `wait_until_done()` in `backup_model.py` ensures the microphone only opens *after* the audio playback finishes.
