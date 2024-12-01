import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


device = "mps" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True,
    chunk_length_s=1
)

def generate_subtitle(audio_file):
    subtitles = pipe(audio_file)
    return subtitles["chunks"]

def transcribe(audio):
    segments = generate_subtitle(audio)
    segments = list(segments)
    for segment in segments:
        # print(segment)
        print("[%.2fs -> %.2fs] %s" %
              (segment["timestamp"][0], segment["timestamp"][1], segment["text"]))
    return segments

if __name__ == "__main__":
    # audio_file = "data/audio/title_1.wav"
    audio_file = "temp_audio.wav"
    subtitle = transcribe(audio_file)
    print(subtitle)