import streamlit as st
from transformers import pipeline
from PIL import Image
from pytubefix import YouTube
from pytubefix.cli import on_progress
import whisper
from whisper.utils import get_writer, WriteSRT
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os.path
import time
from TTS.api import TTS
import torch
import re
import subprocess
import chardet
import moviepy.config as mpy_config
from moviepy.editor import concatenate_audioclips
import pysrt
from moviepy.video.fx.all import speedx

# Uncomment for local deployment/testing
mpy_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']


def fix_srt_encoding(srt_path):
    encoding = detect_encoding(srt_path)
    if encoding.lower() != 'utf-8':
        with open(srt_path, 'r', encoding=encoding) as file:
            content = file.read()
        with open(srt_path, 'w', encoding='utf-8') as file:
            file.write(content)


def add_subtitles_to_video(input_video, subtitle_file, output_video):
    try:
        command = [
            'ffmpeg',
            '-i', f"\"{input_video}\"",
            '-vf', f"subtitles=\"{subtitle_file}\"",
            '-c:a', 'copy',
            output_video
        ]
        subprocess.run(' '.join(command), check=True, shell=True)
        print(f"Subtitles added successfully. Output file: {output_video}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Download progress: {percentage_of_completion:.2f}%")


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def format_timestamp(seconds):
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


@st.cache_resource
def download_model():
    return whisper.load_model("base")


def download_youtube_video(link):
    vid = YouTube(link, on_progress_callback=on_progress)
    sanitized_title = sanitize_filename(vid.title)
    video_path = f"{sanitized_title}.mp4"
    ys = vid.streams.get_highest_resolution()
    ys.download(filename=video_path)
    st.text("Successfully downloaded video")
    return vid.title, video_path


def extract_audio_from_video(video_path, sanitized_title):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_path = f"{sanitized_title}.mp3"
    audio.write_audiofile(audio_path)
    st.text("(1/5) Successfully extracted audio")
    return audio_path


def transcribe_audio_to_srt(engAudioFile, sanitized_title):
    engModel = download_model()
    result = engModel.transcribe(engAudioFile)
    srt_path = f"{sanitized_title}.srt"
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(result["segments"]):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            srt_file.write(f"{text}\n\n")
    st.text("(2/5) Successfully transcibed audio")
    return srt_path


def translate_srt_file(engTextFile, src, dst):
    task_name = f"translation_{src}_to_{dst}"
    model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
    translator = pipeline(task_name, model=model_name, tokenizer=model_name)

    # Open and read the original SRT file
    with open(engTextFile, 'r', encoding='utf-8') as f:
        englishLines = f.read()

    # Split into subtitle blocks (each block contains a timestamp and text)
    blocks = re.split(r'\n\n', englishLines.strip())  # strip extra spaces

    translated_blocks = []
    
    for block in blocks:
        # Split each block into lines
        lines = block.strip().split('\n')
        
        # Ensure block has at least three lines (subtitle number, timestamp, and text)
        if len(lines) < 3:
            continue  # Skip incomplete or improperly formatted blocks
        
        # Extract subtitle number, timestamp, and text
        subtitle_number = lines[0]
        timestamp = lines[1]
        text_lines = lines[2:]

        # Join the text lines and translate
        text_to_translate = ' '.join(text_lines).strip()
        
        if text_to_translate:
            # Translate the text
            translated_text = translator(text_to_translate)[0]["translation_text"]
            translated_block = f"{subtitle_number}\n{timestamp}\n{translated_text}\n"
            translated_blocks.append(translated_block)

    # Write the translated blocks to a new file
    translationText = engTextFile.replace(".srt", " translation.srt")
    with open(translationText, 'w', encoding='utf-8') as n:
        n.write('\n\n'.join(translated_blocks))

    st.text("(3/5) Successfully translated text")
    return translationText


def fix_srt_formatting(translationText):
    with open(translationText, 'r') as file:
        srt_content = file.readlines()

    formatted_subtitles = []
    for entry in srt_content:
        parts = re.split(r'\s+', entry.strip(), maxsplit=4)
        if len(parts) == 5:
            sequence_number, time_start, arrow, time_end, text = parts
            time_start = time_start.replace('.', ',')
            time_end = time_end.replace('.', ',')
            formatted_subtitle = f"{sequence_number}\n{time_start} {arrow} {time_end}\n{text}"
            formatted_subtitles.append(formatted_subtitle)

    fixedText = translationText.replace("translation.srt", "fixed translation.srt")
    with open(fixedText, 'w') as file:
        file.writelines('\n\n'.join(formatted_subtitles))

    with open(fixedText, 'r') as file:
        lines = file.readlines()
    lines = lines[:-3]
    with open(fixedText, 'w') as file:
        file.writelines(lines)

    return fixedText

def generate_translation_audio(fixedText, dst):
    model_name = f"tts_models/{dst}/css10/vits"
    tts = TTS(model_name=model_name, progress_bar=False)

    translation_audio_segments = []
    translationAudio = fixedText.replace(".srt", ".mp3")
    
    # Generate a silent audio clip
    silence_duration = 5  # Duration of silence in seconds
    silence = AudioFileClip("silence.mp3").subclip(0, silence_duration)

    with open(fixedText, 'r') as f:
        lines = f.readlines()

    i = 0
    last_end_time = 0

    while i < len(lines):
        if re.match(r"^\d+$", lines[i].strip()):  # Sequence number
            time_range = lines[i+1].strip()
            text = lines[i+2].strip()

            # Extract start and end times from SRT
            start_time, end_time = time_range.split(" --> ")
            start_secs = convert_srt_time_to_seconds(start_time)
            end_secs = convert_srt_time_to_seconds(end_time)
            duration = end_secs - start_secs

            # Calculate the gap between the end of the last subtitle and the start of the current one
            if i > 0:
                gap = start_secs - last_end_time
                if gap > 0:
                    # Append silence for the gap
                    silence_needed = gap
                    num_silences = int(silence_needed / silence_duration) + 1
                    silence_clip = concatenate_audioclips([silence] * num_silences).subclip(0, silence_needed)
                    translation_audio_segments.append(silence_clip)

            # Generate audio for this subtitle segment
            audio_segment_path = f"temp_segment_{i//4}.mp3"
            tts.tts_to_file(text=text, file_path=audio_segment_path)
            
            # Load the generated audio segment
            audio_segment = AudioFileClip(audio_segment_path)

            # Adjust the audio segment duration to match the subtitle timing
            if audio_segment.duration > duration:
                adjusted_audio_segment = audio_segment.fx(speedx, audio_segment.duration / duration)
            elif audio_segment.duration < duration:
                # Append silence to match the duration
                silence_needed = duration - audio_segment.duration
                num_silences = int(silence_needed / silence_duration) + 1
                silence_clip = concatenate_audioclips([silence] * num_silences).subclip(0, silence_needed)
                adjusted_audio_segment = concatenate_audioclips([audio_segment, silence_clip])
            else:
                adjusted_audio_segment = audio_segment

            # Append to the list of audio segments
            translation_audio_segments.append(adjusted_audio_segment)
            last_end_time = end_secs

            i += 4  # Move to the next subtitle block
        else:
            i += 1

    # Concatenate all audio segments into a single file
    final_audio = concatenate_audioclips(translation_audio_segments)
    final_audio.write_audiofile(translationAudio)

    st.text("(4/5) Successfully generated aligned translated audio")
    return translationAudio




def convert_srt_time_to_seconds(srt_time):
    """Helper function to convert SRT time format (HH:MM:SS,MS) to seconds."""
    time_parts = re.split('[:,]', srt_time)
    hours, minutes, seconds, milliseconds = map(int, time_parts)
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
    return total_seconds


from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx import resize
import textwrap

def wrap_text(text, width):
    """
    Wrap text to fit within a specified width.
    """
    return '\n'.join(textwrap.fill(line, width=width) for line in text.splitlines())

def combine_video_audio_subtitles(video_path, fixedText, translatedAudio, output_vid="output_vid.mp4"):
    video = VideoFileClip(video_path)
    video_width, video_height = video.size
    subtitle_width = int(video_width * 0.9)  # 90% of video width

    subs = pysrt.open(fixedText)
    subtitles = []

    for sub in subs:
        # Get the start and end time for each subtitle
        start_time = sub.start.hours*3600 + sub.start.minutes*60 + sub.start.seconds + sub.start.milliseconds/1000
        end_time = sub.end.hours*3600 + sub.end.minutes*60 + sub.end.seconds + sub.end.milliseconds/1000
        duration = end_time - start_time

        # Wrap the subtitle text
        wrapped_text = wrap_text(sub.text, subtitle_width)

        # Create a TextClip for each subtitle with wrapped text
        subtitle = TextClip(wrapped_text, fontsize=18, color='white', bg_color='black', size=(subtitle_width, None))
        subtitle = subtitle.set_position(('center', 'bottom')).set_duration(duration).set_start(start_time)

        # Append subtitle clip to the list
        subtitles.append(subtitle)

    # Combine video and subtitles
    result = CompositeVideoClip([video] + subtitles)

    # Replace audio of video
    audio = AudioFileClip(translatedAudio)
    translatedVideo = result.set_audio(audio)


    translatedVideo.write_videofile(output_vid)
    
    st.text("(5/5) Added translated subtitles and audio to video")
    
    # Return the path to the output video
    return output_vid




# Main application logic
def main():
    st.title("Foreign Whispers")
    st.header("Welcome to Foreign Whispers. Input your English language YouTube URL and your desired output language. In a few minutes, you will have the video with translated audio and subtitles!")
    link = st.text_input("YouTube URL: ")


    if link:
        try:
            title, video_path = download_youtube_video(link)
        except Exception as e:
            st.error(f"An error occurred downloading the video: {e}")
            return

        if not os.path.exists(video_path):
            st.error(f"Downloaded video file {video_path} does not exist.")
            return

        src = "en"
        lang = st.selectbox("Target language", ["", "Spanish", "French", "Dutch", "Finnish", "Hungarian"])
        lang_map = {"Spanish": "es", "French": "fr", "Dutch": "nl", "Finnish": "fi", "Hungarian": "hu"}
        dst = lang_map.get(lang, '')

        if dst:
            audio_path = extract_audio_from_video(video_path, sanitize_filename(title))
            srt_path = transcribe_audio_to_srt(audio_path, sanitize_filename(title))
            translationText = translate_srt_file(srt_path, src, dst)
            translationAudio = generate_translation_audio(translationText, dst)
            output_vid = combine_video_audio_subtitles(video_path, translationText, translationAudio)

            st.video(output_vid, format="video/mp4", start_time=0)


if __name__ == "__main__":
    main()
