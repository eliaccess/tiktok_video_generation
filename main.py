import json
import logging

from build_video_with_animations import generate_tiktok_video
from generate_images_api import generate_image
from generate_speech import generate_voice
from story_generation import generate_story_full

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

VIDEO_DURATION_MINIMUM = 60

story = {}
security_prompt = "no nudity, no extremely gore content, no violence, no hate speech, no racism, no sexism, no copyrighted material"


def load_story(path_story: str) -> dict:
    logger.info("Loading story data")
    with open(path_story, "r") as file:
        story = json.load(file)
    return story


def generate_images(story: dict) -> None:
    logger.info("Generating images for title page")
    title = story["title"]
    theme = story["theme"]
    summary = story["summary"]
    prompt = f"""
    "general_style": "very realistic, dark ambiance",
    "story": {title},
    "summary": {summary},
    "theme": {theme},
    "security": {security_prompt}"""

    filename = "data/pictures/title.png"
    generate_image(prompt, filename)

    logger.info("Generating images for scenes")

    for scene in story["story"]:
        id = scene["id"]
        scene_description = scene["scene_description"]
        lighting = scene["lighting"]
        details = scene["details"]
        security = security_prompt

        prompt = f"""
        "general_style": "very realistic, dark ambiance",
        "scene_description": "{scene_description}",
        "lighting": "{lighting}",
        "details": "{details}"
        "security": {security}"""

        filename = f"data/pictures/scene_{id}.png"

        generate_image(prompt, filename)
    logger.info("Images generated successfully")


def generate_audio_no_parts(story: dict) -> None:
    logger.info("Generating audio for title page")
    title = story["title"]
    prompt = f"""
    "{title}"""
    filename = "data/audio/title.wav"
    generate_voice(prompt, filename)

    logger.info("Generating audio for scenes")
    for scene in story["story"]:
        id = scene["id"]
        text = scene["text"]

        prompt = f"""
        "{text}"""

        filename = f"data/audio/scene_{id}.wav"

        audio_file_duration = generate_voice(prompt, filename)
    logger.info("Audio generated successfully")


def generate_audio(story: dict) -> None:
    # Calculate how many parts are needed for the title audio
    logger.info("Generating audio for each scene")
    part_counter = 1
    current_duration = 0
    for scene in story["story"]:
        # Generate the current part's title
        id = scene["id"]
        text = scene["text"]

        prompt = f"""
        "{text}"""

        filename = f"data/audio/scene_{id}.wav"

        # Generate the audio for the scene and log its duration
        audio_file_duration = generate_voice(prompt, filename)
        current_duration += audio_file_duration

        if current_duration >= VIDEO_DURATION_MINIMUM:
            part_counter += 1
            current_duration = 0

    if part_counter > 1:
        if current_duration < VIDEO_DURATION_MINIMUM:
            part_counter -= 1
        logger.info(f"Title will be split into {part_counter} parts.")

    logger.info("Generating audio for title page")
    title = story["title"]
    for part in range(1, part_counter + 1):
        part_suffix = f" (part {part})" if part_counter > 1 else ""
        prompt = f'"{title}{part_suffix}"'
        filename = f"data/audio/title_{part}.wav"

        # Generate the audio for the part and get its duration
        audio_file_duration = generate_voice(prompt, filename)

    logger.info("Audio generated successfully")


if __name__ == "__main__":
    # create the needed directories
    import os
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/story", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    os.makedirs("data/pictures", exist_ok=True)
    os.makedirs("data/result", exist_ok=True)
    os.makedirs("data/export", exist_ok=True)
    theme = "horror, suspense, supernatural, parallel world, dark ambiance, immersive, very realistic"
    story_json = generate_story_full(theme)
    story = load_story("data/story/story.json")
    generate_images(story)
    generate_audio(story)
    generate_tiktok_video("data/pictures", "data/audio", "data/result/")
