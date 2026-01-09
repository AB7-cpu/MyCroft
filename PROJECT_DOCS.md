# MyCroft Project - Documentation

## Project Overview
This project is an advanced, voice-first AI assistant designed to perform a wide range of tasks on your local machine. It serves as a "smart co-pilot" that can control windows, play media, answer questions, and manage system information, all through a natural conversational interface.

The assistant is built with **LangGraph** (for agentic workflow), **Groq/Ollama** (for LLM inference), **Whisper** (for speech-to-text), and **VibeVoice** (for local text-to-speech).

## Key Features

### 🗣️ Voice Interaction
-   **Continuous Listening**: Uses **VAD (Voice Activity Detection)** to listen naturally. It waits for you to stop speaking before processing, rather than cutting off after a fixed time.
-   **Real-Time Local TTS**: Uses **VibeVoice** (local WebSocket server) for ultra-low latency speech generation. Nova starts speaking while still "thinking" about the rest of the response.
-   **Streaming Architecture**: Leveraging LangGraph's `astream`, the assistant processes and speaks sentences as they are generated, rather than waiting for the full response.
-   **Conversation Awareness**: Retains context of the current session thread.

### 🛠️ Capabilities (Tools)
The assistant is equipped with the following tools (`tools.py`):
1.  **YouTube Player** (`play_on_yt`): Plays videos or songs directly on YouTube.
2.  **Web Search** (`TavilySearch`): Performs real-time web searches for up-to-date information.
3.  **Window Management** (`window_tool`): List, focus, minimize, maximize, close, and screenshot specific windows.
4.  **System Information** (`get_system_info`): Checks Battery status and Wi-Fi connection.
5.  **WLED Control** (`control_wled`): Controls RGB LED strips (via WLED interface).

### 🧠 Intelligence
-   **Dual Model Architecture**:
    -   **Primary**: `openai/gpt-oss-20b` (via Groq) for high-speed, high-quality reasoning.
    -   **Fallback**: `qwen3:4b` (via Ollama) for local, offline backup.
-   **Agentic Framework**: Uses **LangGraph** `create_react_agent` to reason about when to use tools vs. when to just chat.

## Setup & Usage

### Prerequisites
-   Python 3.10+
-   Virtual Environment (`venv`)
-   **API Keys** (in `.env`):
    -   `GROQ_API_KEY`
    -   `TAVILY_API_KEY`

### Installation
1.  Activate the virtual environment:
    ```powershell
    .\venv\Scripts\activate
    ```
2.  Install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```

### Running the Assistant
You need to run **two** components:

1.  **Start VibeVoice Server**:
    ```powershell
    cd required_repos/VibeVoice
    python .\demo\vibevoice_realtime_demo.py
    ```
2.  **Start MyCroft (Main Loop)**:
    ```powershell
    # In another terminal window
    python backup_model.py
    ```

### Controls
-   **Wake Word**: Say "**Hey Mycroft**" to wake up MyCroft.
-   **Follow-up Mode**: MyCroft stays active for a few seconds after replying, allowing for continuous conversation.
-   **Visual Feedback**:
    -   **Cyan**: MyCroft is listening.
    -   **Preset 1**: MyCroft is sleeping.

## Project Structure
-   **`backup_model.py`**: **[ENTRY POINT]** The main async runner containing the streaming loop and agent logic.
-   **`tts.py`**: Manages the persistent WebSocket connection to VibeVoice and real-time audio buffering.
-   **`stt_vad.py`**: Handles Voice Activity Detection (VAD) and Whisper transcription.
-   **`tools.py`**: Definitions of all capabilities (YouTube, Windows, etc.).
-   **`wakeword.py`**: listnes for "Hey Mycroft" using `openwakeword`.
