# Research & Experiments

This directory contains experimental code and models used to evaluate different technologies before integrating them into the main assistant.

## Directory Structure

### 1. `wake_word/`
*   **Purpose**: Testing low-latency wake word detection.
*   **Key File**: `wake_word_test.py`
*   **Technology**: `openwakeword` (ONNX based).
*   **Status**: **Adopted**.
    *   Verified "Hey Mycroft" model.
    *   Integrated into `wakeword.py` and `backup_model.py`.

### 2. `speech_to_text/`
*   **Purpose**: Evaluating transcription accuracy and speed.
*   **Key File**: `main.py`
*   **Technology**: `openai-whisper` (Original PyTorch implementation).
*   **Status**: **Evolution**.
    *   Started with `whisper` (small model).
    *   Project upgraded to `faster_whisper` in `stt_vad.py` for better performance on GPU (`float16`).

### 3. `text_to_speech/`
*   **Purpose**: Finding high-quality, emotive TTS.
*   **Subdirectories**:
    *   `OpenVoice/`: Experiments with OpenVoice (cost-effective cloning).
    *   `StyleTTS2/`: Experiments with StyleTTS2 (high fidelity).
*   **Status**: **On Hold / Alternative Selected**.
    *   Currently using **PlayAI** (via Groq) in `tts.py` for the best balance of speed and quality without heavy local VRAM usage.

## Notes
*   **`audio.mp3`**: Sample audio used for testing Whisper transcription.
*   **`.text_to_speech`**: Likely a hidden cache or config directory for TTS models.
