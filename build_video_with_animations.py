# For moviepy version 2.1.1 and newest version of PIL
import logging
import random

import cv2
import numpy as np
from moviepy import AudioFileClip, ImageClip, VideoClip, concatenate_videoclips

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

FPS = 24
RESOLUTION = (1080, 1920)
VIDEO_DURATION_MINIMUM = 60


def add_effects_to_image(image_clip: ImageClip, duration: float) -> VideoClip:
    """
    Apply random zoom and rotation to an image, gradually over its own duration.
    """
    # Generate random values for each clip
    rotation_angle = random.uniform(-2, 2)  # Rotate between -10° and 10°

    def apply_transform(get_frame, t):
        """
        Apply rotation and zoom relative to time `t` for the clip.
        """
        progress = t / duration  # Normalize time to a [0, 1] range for the clip
        current_rotation = rotation_angle * progress

        # Get current frame and apply transformations
        frame = get_frame(t)
        rotated_frame = ImageClip(frame).rotated(current_rotation).get_frame(t)
        # rotated_frame = ImageClip(frame).get_frame(t)
        # zoomed_frame = ImageClip(rotated_frame).resized((int(w* 3), int(h* 3)), apply_to_mask=False).get_frame(t)
        zoomed_frame = rotated_frame
        return zoomed_frame

    # Apply transformations to the clip
    return image_clip.transform(apply_transform)


def Zoom(clip: ImageClip, mode="in", position="center", zoom_factor=1):
    fps = FPS
    duration = clip.duration
    total_frames = int(duration * fps)

    # Calculate speed dynamically based on zoom_factor and duration
    speed = zoom_factor / duration

    def main(getframe, t):
        frame = getframe(t)
        h, w = frame.shape[:2]
        i = t * fps

        if mode == "out":
            i = total_frames - i

        # Compute zoom level
        zoom = 1 + (i * ((0.1 * speed) / total_frames))

        # Define positions
        positions = {
            "center": [(w - (w * zoom)) / 2, (h - (h * zoom)) / 2],
            "left": [0, (h - (h * zoom)) / 2],
            "right": [(w - (w * zoom)), (h - (h * zoom)) / 2],
            "top": [(w - (w * zoom)) / 2, 0],
            "topleft": [0, 0],
            "topright": [(w - (w * zoom)), 0],
            "bottom": [(w - (w * zoom)) / 2, (h - (h * zoom))],
            "bottomleft": [0, (h - (h * zoom))],
            "bottomright": [(w - (w * zoom)), (h - (h * zoom))],
        }

        # Translation offsets
        tx, ty = positions[position]

        # Transformation matrix
        M = np.array([[zoom, 0, tx], [0, zoom, ty]])
        frame = cv2.warpAffine(frame, M, (w, h))
        return frame

    return clip.transform(main)


def ZoomAndRotate(
    clip, mode="in", position="center", zoom_factor=0.7, rotation_factor=2
):
    fps = FPS
    duration = clip.duration
    total_frames = int(duration * fps)

    # randomly select a rotation direction
    rotation_factor = random.choice([-rotation_factor, rotation_factor])

    # Calculate speed dynamically based on zoom_factor and duration
    speed = zoom_factor / duration

    def main(get_frame, t):
        # Get the current frame at time `t`
        frame = get_frame(t)
        h, w = frame.shape[:2]
        i = t * fps

        if mode == "out":
            i = total_frames - i

        # Compute zoom level
        zoom = 1.1 + (i * ((0.1 * speed) / total_frames))

        # Compute rotation angle (in degrees)
        rotation_angle = (
            i / total_frames
        ) * rotation_factor  # Rotate up to `rotation_factor` degrees
        if mode == "out":
            rotation_angle = -rotation_angle

        # Adjust zoom to prevent background exposure during rotation
        angle_radians = np.deg2rad(abs(rotation_angle))
        extra_zoom = (np.sin(angle_radians) + np.cos(angle_radians)) / np.sqrt(2)
        safety_zoom = max(1, extra_zoom)
        zoom = max(zoom, safety_zoom)

        # Define positions for translation offsets
        positions = {
            "center": [(w - (w * zoom)) / 2, (h - (h * zoom)) / 2],
            "left": [0, (h - (h * zoom)) / 2],
            "right": [(w - (w * zoom)), (h - (h * zoom)) / 2],
            "top": [(w - (w * zoom)) / 2, 0],
            "topleft": [0, 0],
            "topright": [(w - (w * zoom)), 0],
            "bottom": [(w - (w * zoom)) / 2, (h - (h * zoom))],
            "bottomleft": [0, (h - (h * zoom))],
            "bottomright": [(w - (w * zoom)), (h - (h * zoom))],
        }

        # Calculate translation offsets
        tx, ty = positions[position]

        # Create zoom and rotation matrix
        center = (w / 2, h / 2)
        M_zoom = np.array([[zoom, 0, tx], [0, zoom, ty]])
        M_rotate = cv2.getRotationMatrix2D(center, rotation_angle, 1)

        # Combine the zoom and rotation matrices
        M_combined = np.vstack([M_rotate, [0, 0, 1]]) @ np.vstack([M_zoom, [0, 0, 1]])
        M_final = M_combined[:2, :]

        # Apply the combined transformation
        frame = cv2.warpAffine(frame, M_final, (w, h))
        return frame

    # Ensure the transform is applied frame by frame
    return clip.transform(main)


def prepare_tiktok_clip(image_file, audio_file):
    """
    Prepare a single TikTok-style clip with an image, animation, and audio.
    """
    # Load audio
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration

    # Load and resize image to fit TikTok's vertical format
    image_clip = ImageClip(image_file).with_duration(duration)
    image_clip = image_clip.resized(height=RESOLUTION[1]).with_position(
        ("center", "center")
    )

    # Apply effects to the image
    image_clip = ZoomAndRotate(image_clip)
    # image_clip = add_effects_to_image(image_clip, duration)

    # Combine image and audio
    return image_clip.with_audio(audio_clip)


def sort_by_number(file_list):
    """
    Sort a list of file names based on the numeric part in the name.
    """
    import re

    return sorted(file_list, key=lambda x: int(re.search(r"\d+", x).group()))


def create_tiktok_video_no_parts(
    image_files, audio_files, output_file="tiktok_video.mp4"
):
    """
    Create a TikTok-friendly video by combining images and audio.
    """
    clips = []

    # Separate title image and audio
    image_title_file = [f for f in image_files if f.endswith("title.png")][0]
    audio_title_file = [f for f in audio_files if f.endswith("title.wav")][0]

    # Remove title image from the list
    image_files = [f for f in image_files if f != image_title_file]
    audio_files = [f for f in audio_files if f != audio_title_file]

    # Add title clip
    title_clip = prepare_tiktok_clip(image_title_file, audio_title_file)
    clips.append(title_clip)

    image_files = sort_by_number(image_files)
    audio_files = sort_by_number(audio_files)

    for image_file, audio_file in zip(image_files, audio_files):
        tiktok_clip = prepare_tiktok_clip(image_file, audio_file)
        clips.append(tiktok_clip)

    # Concatenate all clips into a final video
    final_video = concatenate_videoclips(clips)

    # Save the output video
    final_video.write_videofile(
        output_file,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4,
    )


def create_tiktok_videos(
    image_files,
    audio_files,
    output_directory="output_videos",
    video_duration_minimum=VIDEO_DURATION_MINIMUM,
):
    """
    Create TikTok-friendly videos by combining images and audio for each part.
    """
    import os

    os.makedirs(output_directory, exist_ok=True)  # Ensure the output directory exists

    clips = []
    part_counter = 1
    current_duration = 0.0

    # Separate title image and audio
    image_title_file = [f for f in image_files if f.endswith("title.png")][0]
    title_audio_files = sorted(
        [f for f in audio_files if f.startswith("data/audio/title_")]
    )

    # Remove title image from the list
    image_files = [f for f in image_files if f != image_title_file]
    audio_files = [f for f in audio_files if f not in title_audio_files]

    # Sort images and audio files numerically
    image_files = sort_by_number(image_files)
    audio_files = sort_by_number(audio_files)

    # Create videos for each part
    for title_audio_file in title_audio_files:
        # Add title clip
        title_clip = prepare_tiktok_clip(image_title_file, title_audio_file)
        clips = [title_clip]  # Start the clips list with the title clip
        current_duration = title_clip.duration

        # Add scene clips until the minimum duration is reached
        while current_duration < video_duration_minimum and image_files and audio_files:
            image_file = image_files.pop(0)
            audio_file = audio_files.pop(0)
            scene_clip = prepare_tiktok_clip(image_file, audio_file)
            clips.append(scene_clip)
            current_duration += scene_clip.duration

        # Create video for the current part
        output_file = os.path.join(output_directory, f"tiktok_part_{part_counter}.mp4")
        final_video = concatenate_videoclips(clips)
        final_video.write_videofile(
            output_file,
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=4,
        )
        logger.info(f"Created video part {part_counter}: {output_file}")
        part_counter += 1

    logger.info("All TikTok videos have been created successfully.")


def generate_tiktok_video(path_images: str, path_audio: str, output_file: str):
    import glob

    # Collect image and audio files sorted by name
    image_files = glob.glob(f"{path_images}/*.png")
    audio_files = glob.glob(f"{path_audio}/*.wav")

    create_tiktok_videos(image_files, audio_files, output_directory=output_file)


# Example usage
if __name__ == "__main__":
    generate_tiktok_video("data/pictures", "data/audio", "data/result/")
