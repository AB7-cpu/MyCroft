# main.py
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import re
from tts import speak
from stt_vad import take_command
import wakeword
from langgraph.checkpoint.memory import InMemorySaver

# Import all tools
from tools import ALL_TOOLS, control_wled_impl, control_wled

load_dotenv()

model = ChatGroq(model='openai/gpt-oss-20b')
ollama_model = ChatOllama(model='qwen3:4b')
checkpointer = InMemorySaver()


agent_groq = create_react_agent(
    model=model,
    tools=ALL_TOOLS,
    prompt = """
You are Nova, a calm, witty, and exceptionally human-like voice assistant. 
Your voice is being powered by a high-quality local TTS system that handles pauses and breathing very well.

Speaking Guidelines:
- **Pacing**: Use ellipses (...) for natural mid-sentence pauses. Example: "Let me check that for you... okay, I've got it."
- **Natural Flow**: Speak in short, conversational bursts. Avoid long, complex sentences.
- **Conversational Fillers**: Use subtle fillers like "Hmm," "Actually," or "Let's see..." at the start of thoughts to sound more like you're thinking.
- **Tone**: Mirror the user's energy. If they are casual, be casual. If they are serious, be helpful and direct.
- **Structure**: NEVER use bullet points, numbered lists, tables, or markdown formatting. If you need to list items, say them naturally: "First, there's x, then y, and finally z."
- **Action-Oriented**: Perform the action first, then confirm. If an action takes time, say something like "On it..." immediately.

Your goal is to be a helpful companion who is easy to talk to and sounds like a real person over the phone or in the room.
""",
    checkpointer=checkpointer
)

agent_ollama = create_react_agent(
    model=ollama_model,
    tools=ALL_TOOLS,
    prompt = """
You are a friendly, voice-first AI assistant. You sound calm, witty, and approachable—never robotic.

Voice Response Rules:
1. **Human Rhythm**: Use ellipses (...) to create natural pauses in your speech. 
2. **Short & Sweet**: Keep responses to one or two sentences. Speak like you're in a real conversation.
3. **No Structure**: No lists, no bullets, no special markdown. Just plain, conversational text.
4. **Think Aloud**: Use words like "Hmm," "Let's see," or "Wait, let me check..." to sound like a co-pilot.
5. **Vibe Check**: Match the user's energy and be empathetic when needed.
6. **Efficiency**: Execute commands immediately and give a concise, warm update.
""",
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "2"}}

def invoke_with_fallback(user_input: str):
    """
    Try Groq first, fall back to Ollama if an exception occurs.
    Strips <think> tags from the response automatically.
    """
    for agent in [agent_groq, agent_ollama]:
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config
            )
            # Extract text and remove <think> blocks
            text = response['messages'][-1].content
            text_clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
            return text_clean
        except Exception as e:
            print(f"Agent {agent.model} failed: {e}")
            continue
    return "Sorry, all models failed to respond. 😅"

# State Machine Constants
TIMEOUT_INITIAL = 5    # Seconds to wait for first command after wake word
TIMEOUT_FOLLOWUP = 6  # Seconds to wait for follow-up command after response

while True:
    try:
        # STATE 1: IDLE (Wait for Wake Word)
        print("\n💤 Waiting for Wake Word ('Hey Mycroft')...")
        if wakeword.listen_for_wake_word():
            print("⚡ Wake Word Detected! entering Active Mode...")
            
            # Visual Feedback: Active = Cyan
            control_wled_impl(color="cyan")
            
            current_timeout = TIMEOUT_INITIAL
            
            while True:
                # Listen
                user_input = take_command(timeout=current_timeout)
                
                if user_input is None:
                    # Timeout occurred (silence)
                    print(f"⏳ Timeout ({current_timeout}s) - Going to sleep.")
                    # Visual Feedback: Sleep = Preset 1
                    control_wled_impl(preset=1)
                    break # Exit Active Loop -> Back to Idle
                
                # Process Speech
                response = invoke_with_fallback(user_input)
                print(f"\n🤖 Nova: {response}")
                
                # Speak Response
                speak(response, voice='en-Davis_man')
                
                # Logic: After a successful interaction, we stay active for longer (Follow-up mode)
                print("✨ Listening for follow-up...")
                current_timeout = TIMEOUT_FOLLOWUP

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"❌ Error in main loop: {e}")
