from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import pathlib
from scipy.io.wavfile import write

config = XttsConfig()
path_to_xtts = "/Users/elimouni/Desktop/XTTS-v2"
config_path = pathlib.Path(path_to_xtts + "/config.json")
config.load_json(config_path)
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir=path_to_xtts, eval=True)
model.to("mps")

def generate_voice(prompt, output_name):
    outputs = model.synthesize(
        prompt,
        config,
        speaker_wav=path_to_xtts+"/samples/en_sample.wav",
        gpt_cond_len=3,
        language="en",
    )

    output_file_path = f'{output_name}.wav'
    write(output_file_path, 24000, outputs['wav'])


if __name__ == "__main__":
    prompt = "The air was thick with the scent of salt as Lily and her friends stepped off the ferry, the vibrant blue ocean stretching endlessly behind them."
    output_name = "data/audio/output_name"
    generate_voice(prompt, output_name)