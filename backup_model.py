from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import asyncio
import re
from tts import speak_async, start_stream, stop_stream, wait_until_done
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
1. **Short & Sweet**: Keep responses to one or two sentences. Speak like you're in a real conversation.
2. **No Structure**: No lists, no bullets, no special markdown. Just plain, conversational text.
3. **Think Aloud**: Use words like "Hmm," "Let's see," or "Wait, let me check..." to sound like a co-pilot.
4. **Vibe Check**: Match the user's energy and be empathetic when needed.
5. **Efficiency**: Execute commands immediately and give a concise, warm update.
""",
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "2"}}

def clean_text_for_tts(text: str) -> str:
    """Removes markdown and other TTS-unfriendly characters."""
    # Remove ellipses (user requested)
    text = text.replace('...', ' ').replace('..', ' ')
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`.*?`', '', text)
    # Remove bold/italic
    text = re.sub(r'\*\*|\*', '', text)
    # Remove think blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Clean up excess whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def stream_with_fallback(user_input: str):
    """
    Streams updates from Groq, falls back to Ollama if an error occurs.
    Eliminates <think> tags from the stream.
    """
    for agent in [agent_groq, agent_ollama]:
        try:
            full_response = ""
            in_think_block = False
            
            async for event in agent.astream(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
                stream_mode="messages"
            ):
                chunk, metadata = event
                if metadata.get("langgraph_node") == "agent":
                    content = chunk.content
                    if not content:
                        continue
                        
                    if "<think>" in content:
                        in_think_block = True
                        content = content.split("<think>")[-1]
                    if "</think>" in content:
                        in_think_block = False
                        content = content.split("</think>")[-1]
                    
                    if not in_think_block and content:
                        yield content
                        full_response += content
            
            if full_response:
                return 
        except Exception as e:
            print(f"Agent failed: {e}")
            continue
    yield "Sorry, all models failed to respond... 😅"

async def tts_consumer(queue):
    """Consumes sentences from the queue and speaks them."""
    while True:
        sentence = await queue.get()
        if sentence is None:
            break
        
        # Final cleanup for TTS
        clean_sentence = clean_text_for_tts(sentence)
        if clean_sentence:
            print(f"\n🎙️ Speaking: {clean_sentence}")
            await speak_async(clean_sentence, voice='en-Davis_man')
        
        queue.task_done()

async def process_and_speak(user_input):
    """Streams from LLM, buffers sentences, and feeds them to TTS."""
    queue = asyncio.Queue()
    consumer_task = asyncio.create_task(tts_consumer(queue))
    
    sentence_buffer = ""
    print("\n🤖 Nova: ", end="", flush=True)
    
    async for chunk in stream_with_fallback(user_input):
        print(chunk, end="", flush=True)
        sentence_buffer += chunk
        
        # Robust sentence splitting:
        # 1. Look for . ! ? or \n
        # 2. Ensure it's not preceded by a digit (avoid splitting 4.2)
        # 3. Ensure it's followed by a space or end of stream
        if any(p in chunk for p in ".!?\n"):
            # Split only on punctuation NOT preceded by a digit, followed by whitespace
            parts = re.split(r'(?<=[^0-9][.!?\n])\s+', sentence_buffer)
            
            if len(parts) > 1:
                # Keep the last part in buffer as it might be incomplete
                sentence_buffer = parts.pop()
                for part in parts:
                    if part.strip():
                        await queue.put(part)
    
    # Final flush
    if sentence_buffer.strip():
        await queue.put(sentence_buffer)
    
    print() 
    await queue.put(None) 
    await consumer_task

async def main_loop():
    TIMEOUT_INITIAL = 5    
    TIMEOUT_FOLLOWUP = 6  

    start_stream() # Initialize hardware early

    while True:
        try:
            print("\n💤 Waiting for Wake Word ('Hey Mycroft')...")
            if await asyncio.to_thread(wakeword.listen_for_wake_word):
                print("⚡ Wake Word Detected! entering Active Mode...")
                control_wled_impl(color="cyan")
                
                current_timeout = TIMEOUT_INITIAL
                
                while True:
                    user_input = await asyncio.to_thread(take_command, timeout=current_timeout)
                    
                    if user_input is None:
                        print(f"⏳ Timeout ({current_timeout}s) - Going to sleep.")
                        control_wled_impl(preset=1)
                        break 
                    
                    # Process and Speak
                    await process_and_speak(user_input)
                    
                    # Wait for TTS to finish to avoid hearing self
                    await wait_until_done()
                    
                    print("✨ Listening for follow-up...")
                    current_timeout = TIMEOUT_FOLLOWUP

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")

    stop_stream()

if __name__ == "__main__":
    asyncio.run(main_loop())
