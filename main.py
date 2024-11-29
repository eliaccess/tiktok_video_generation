import json
import logging

from build_video_with_animations import generate_tiktok_video
from generate_images_api import generate_image
from generate_speech import generate_voice
from story_generation import generate_story_full

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
    prompt = f"""
    "general_style": "very realistic, dark ambiance",
    "story": {title},
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


def generate_audio(story: dict) -> None:
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

        generate_voice(prompt, filename)
    logger.info("Audio generated successfully")


if __name__ == "__main__":
    theme = "horror, ghost, vacation"
    story_json = generate_story_full(theme)
    story = load_story("data/story.json")
    generate_images(story)
    generate_audio(story)
    generate_tiktok_video("data/pictures", "data/audio", "data/result/final_video")
