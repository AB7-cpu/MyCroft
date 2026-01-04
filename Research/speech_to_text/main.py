import whisper
import torch


device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)
model = whisper.load_model("small").to(device)

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("F:\\Project\\The_Ultimate_Assistant_Project\\Research\\speech_to_text\\audio.mp3")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)