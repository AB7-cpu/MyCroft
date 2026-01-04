# Research & Experiments

This directory contains experimental code and models used to evaluate different technologies before integrating them into the main assistant.

## Technology Evolution

### 1. Wake Word Detection
*   **Technology**: [openWakeWord](https://github.com/dscripka/openWakeWord) (ONNX based).
*   **History**: First model explored and adopted.
*   **Status**: **Adopted**.
    *   Provides high reliability and low latency.
    *   Integrated into `wakeword.py` and `backup_model.py`.

### 2. Speech to Text (STT)
*   **Technologies**:
    *   [SpeechRecognition](https://github.com/Uberi/speech_recognition) (.recognize_google())
    *   [Whisper](https://github.com/openai/whisper) (small model)
    *   [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (medium model, GPU)
*   **History**:
    1.  Started with `SpeechRecognition` using Google's API.
    2.  **Challenge**: High latency made real-time interaction difficult.
    3.  Evaluated `Whisper` (small) for local processing.
    4.  Upgraded to `faster-whisper` (medium) for optimal performance.
*   **Status**: **Adopted**.
    *   Currently using `faster_whisper` in `stt_vad.py` with `float16` on CUDA.

### 3. Text to Speech (TTS)
*   **Technologies**:
    *   [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
    *   [OpenVoice](https://github.com/myshell-ai/OpenVoice)
    *   [StyleTTS2](https://github.com/yl4579/StyleTTS2)
    *   [Coqui XTTS2](https://github.com/coqui-ai/TTS)
    *   [VibeVoice](https://github.com/microsoft/VibeVoice)
*   **History**:
    1.  Started with `pyttsx3`.
    2.  **Challenge**: Fast but robotic and unnatural.
    3.  Explored `StyleTTS2` and `OpenVoice`.
    4.  Used `OpenVoice` for a while until discovering `Coqui XTTS2`.
    5.  **Challenge**: `XTTS2` provided great natural voices but had streaming difficulties.
    6.  Adopted `VibeVoice` for current implementation.
*   **Status**: **Adopted (Local)**.
    *   Using local `VibeVoice` via WebSocket streaming in `tts.py`.

## Directory Structure
*   `wake_word/`: Testing low-latency wake word detection.
*   `speech_to_text/`: Evaluating transcription accuracy and speed.
*   `text_to_speech/`: Finding high-quality, emotive TTS. Includes experiments with `OpenVoice`, `StyleTTS2`, etc.

## Notes
*   **`audio.mp3`**: Sample audio used for testing Whisper transcription.
