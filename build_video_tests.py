from moviepy import AudioFileClip, ImageClip, VideoClip, concatenate_videoclips
from moviepy.video.fx.Resize import Resize
import random

def add_effects_to_image(image_clip: ImageClip, duration: float) -> VideoClip:
    """
    Apply random zoom and rotation to an image, gradually over its own duration.
    """
    # Generate random values for each clip
    rotation_angle = random.uniform(-2, 2)  # Rotate between -10° and 10°
    zoom_start = 1.5  # Start with normal size
    zoom_end = random.uniform(1.9, 2.2)  # Slightly zoom in (or out)

    def apply_transform(get_frame, t):
        """
        Apply rotation and zoom relative to time `t` for the clip.
        """
        progress = t / duration  # Normalize time to a [0, 1] range for the clip
        current_rotation = rotation_angle * progress
        current_zoom = zoom_start + (zoom_end - zoom_start) * progress

        # Get current frame and apply transformations
        frame = get_frame(t)
        h, w, _ = frame.shape
        rotated_frame = ImageClip(frame).rotated(current_rotation).get_frame(t)
        # zoomed_frame = ImageClip(rotated_frame).resized((int(w* 3), int(h* 3)), apply_to_mask=False).get_frame(t)
        zoomed_frame = rotated_frame
        return zoomed_frame

    # Apply transformations to the clip
    return image_clip.transform(apply_transform)


def prepare_tiktok_clip(image_file, audio_file):
    """
    Prepare a single TikTok-style clip with an image, animation, and audio.
    """
    # Load audio
    audio_clip = AudioFileClip(audio_file)
    duration = audio_clip.duration

    # Load and resize image to fit TikTok's vertical format
    image_clip = ImageClip(image_file).with_duration(duration)
    image_clip = image_clip.resized(height=480).with_position(("center", "center"))

    # Apply effects to the image
    image_clip = add_effects_to_image(image_clip, duration)

    # Combine image and audio
    return image_clip.with_audio(audio_clip)

def sort_by_number(file_list):
    """
    Sort a list of file names based on the numeric part in the name.
    """
    import re
    return sorted(file_list, key=lambda x: int(re.search(r'\d+', x).group()))

def create_tiktok_video(image_files, audio_files, output_file="tiktok_video.mp4"):
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
        output_file, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", threads=4
    )

def generate_tiktok_video(path_images: str, path_audio: str, output_file: str):
    import glob

    # Collect image and audio files sorted by name
    image_files = glob.glob(f"{path_images}/*.png")
    audio_files = glob.glob(f"{path_audio}/*.wav")

    create_tiktok_video(image_files, audio_files, output_file=f"{output_file}.mp4")

# Example usage
if __name__ == "__main__":
    generate_tiktok_video("data/pictures", "data/audio", "data/result/final_video")