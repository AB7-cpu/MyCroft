from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

speakers = ['Dionisio Schuyler', 'Ludvig Milivoj', 'Luis Moray', 'Baldur Sanjin', 'Damjan Chapman', 'Nova Hogarth']

text = """Okay — one last thing.

I’ve saved your progress, but I haven’t submitted it yet.
If you’d like to make changes, now would be a good time.

Should I go ahead and finish it for you?
"""


for i, speak in enumerate(speakers):
    file_name = speak.replace(" ", "_")
    tts.tts_to_file(
        text=text,
        speaker=speak,
        language="en",
        file_path=f"best_short_listed/{file_name}.wav"
    )

    print(f"Completed testing speaker {i}) {speak}")