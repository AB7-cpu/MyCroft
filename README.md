# 🎙️ MyCroft (aka Nova)

Welcome to the **MyCroft**, a powerful, low-latency, voice-first AI "co-pilot" for your Windows machine. MyCroft isn't just a chatbot; she has eyes, ears, and hands—capable of controlling your desktop, searching the web, and providing natural, real-time spoken feedback using local AI models.


## 🚀 Key Highlights

-   **Zero-Latency Speech**: Powered by a local **VibeVoice** WebSocket server, MyCroft speaks as she thinks, with no cloud delays.
-   **True Conversation**: Using **Voice Activity Detection (VAD)** and **Faster-Whisper**, you can talk to MyCroft naturally without pressing buttons or waiting for timers.
-   **Agentic Power**: Built on **LangGraph**, Nova knows when to use tools (YouTube, Windows Control, WLED) and when to simply chat.
-   **Privacy-First**: Most of the heavy lifting (STT, TTS, Fallback LLM) happens directly on your machine.

---

## 🛠️ Tech Stack

-   **Orchestration**: LangGraph
-   **LLMs**: Groq (Cloud / Speed) & Ollama (Local / Fallback)
-   **Speech-to-Text**: WebRTC VAD + Faster-Whisper
-   **Text-to-Speech**: VibeVoice (Local streaming)
-   **Environment**: Python 3.10+

---

## 📖 Essential Documentation

For detailed information, please refer to the following guides:

1.  **[User & Setup Guide](PROJECT_DOCS.md)**: How to install, configure API keys, and run MyCroft for the first time.
2.  **[Developer Guide](DEVELOPER_GUIDE.md)**: Architecture deep-dive, component breakdown, and technical history.

---

## 🏁 Quick Start

1.  **Environment Setup**:
    ```powershell
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Run VibeVoice Server**:
    ```powershell
    cd required_repos/VibeVoice
    python .\demo\vibevoice_realtime_demo.py
    ```
3.  **Run MyCroft**:
    ```powershell
    python backup_model.py
    ```

---

## 💡 Usage Tips

-   Say "**Hey Mycroft**" to wake her up.
-   MyCroft stays in "listening mode" after her response to make follow-ups easier.
-   If MyCroft starts reading code or markdown, don't worry—the new text cleaner automatically strips that for a better voice experience.

---

