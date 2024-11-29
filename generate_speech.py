import pathlib

from scipy.io.wavfile import write
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

config = XttsConfig()
path_to_xtts = "/Users/elimouni/Desktop/XTTS-v2"
config_path = pathlib.Path(path_to_xtts + "/config.json")
config.load_json(config_path)
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir=path_to_xtts, eval=True)
model.to("mps")


def generate_voice(prompt, output_name) -> float:
    outputs = model.synthesize(
        prompt,
        config,
        speaker_wav=path_to_xtts + "/samples/en_sample.wav",
        gpt_cond_len=3,
        language="en",
    )

    output_file_path = f"{output_name}"
    sampling_rate = 24000  # Assuming the sampling rate is 24 kHz
    write(output_file_path, sampling_rate, outputs["wav"])

    # Calculate duration in seconds
    audio_length = len(outputs["wav"])
    duration = audio_length / sampling_rate

    return duration


if __name__ == "__main__":
    prompt = "The air was thick with the scent of salt as Lily and her friends stepped off the ferry, the vibrant blue ocean stretching endlessly behind them."
    output_name = "data/audio/output_name.wav"
    generate_voice(prompt, output_name)
