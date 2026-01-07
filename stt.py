# listener.py
import speech_recognition as sr

r = sr.Recognizer()

def take_command(timeout=5, phrase_time_limit=10):
    """Listen to the user's voice and return recognized text or None."""
    try:
        with sr.Microphone() as source:
            # Calibrate once for background noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("🎙️ Listening...")
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

        # Try to recognize speech
        text = r.recognize_google(audio)
        print(f"✅ Heard: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        print("⏳ No speech detected.")
    except sr.UnknownValueError:
        print("🤔 Couldn't understand.")
    except sr.RequestError:
        print("⚠️ Speech service unavailable.")
    except Exception as e:
        print("❌ Error:", e)

    return None
