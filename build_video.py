from moviepy import AudioFileClip, ImageClip, concatenate_videoclips


def create_video(image_files, audio_files, output_file="output_video.mp4"):
    clips = []

    for image_file, audio_file in zip(image_files, audio_files):
        # Load image and audio
        image_clip = ImageClip(image_file).with_duration(
            AudioFileClip(audio_file).duration
        )
        audio_clip = AudioFileClip(audio_file)
        # Combine image with its audio
        video_clip = image_clip.with_audio(audio_clip)
        clips.append(video_clip)

    # Concatenate all clips
    final_video = concatenate_videoclips(clips)

    # Write the result to a file
    final_video.write_videofile(output_file, fps=24, codec="libx264", audio_codec="aac")


# Example usage
if __name__ == "__main__":
    import glob

    # Collect image and audio files sorted by name
    image_files = sorted(glob.glob("data/pictures/*.png"))
    audio_files = sorted(glob.glob("data/audio/*.wav"))

    create_video(image_files, audio_files, output_file="data/result/final_video.mp4")
