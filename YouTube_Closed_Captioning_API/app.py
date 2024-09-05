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

# Set the path to the ImageMagick binary
mpy_config.change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})


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
    st.text("Successfully extracted audio")
    return audio_path


def transcribe_audio_to_srt(engAudioFile, sanitized_title):
    engModel = download_model()
    result = engModel.transcribe(engAudioFile)
    srt_path = f"{sanitized_title}.srt"
    with open(srt_path, 'w') as srt_file:
        for i, segment in enumerate(result["segments"]):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            srt_file.write(f"{text}\n\n")
    st.text("Successfully transcibed audio")
    return srt_path


def translate_srt_file(engTextFile, src, dst):
    task_name = f"translation_{src}_to_{dst}"
    model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"
    translator = pipeline(task_name, model=model_name, tokenizer=model_name)

    with open(engTextFile, 'r') as f:
        englishLines = f.read()
        lines = re.split(r'\n\n', englishLines)
        translatedLines = [translator(line)[0]["translation_text"] + '\n' for line in lines]

    translationText = engTextFile.replace(".srt", " translation.srt")
    with open(translationText, 'w') as n:
        for line in translatedLines:
            n.write(line)
    st.text("Successfully translated text")
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
    translationAudio = fixedText.replace(".srt", ".mp3")

    tts = TTS(model_name=model_name, progress_bar=False)
    with open(fixedText, 'r') as f:
        txt = f.read()
        tts.tts_to_file(text=txt, file_path=translationAudio)
    st.text("Successfully generated translated audio")
    return translationAudio


def combine_video_audio_subtitles(video_path, fixedText, translatedAudio, output_vid="output_vid.mp4"):
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=28, color='white')
    subs = SubtitlesClip(fixedText, generator)
    video = VideoFileClip(video_path)
    result = CompositeVideoClip([video, subs.set_position(("center", "bottom"))])

    audio = AudioFileClip(translatedAudio)
    try:
        video_clip = VideoFileClip(output_vid)
    except Exception as e:
        print(f"Failed to load the video file: {e}")
        exit()

    translatedVideo = video_clip.set_audio(audio)
    translatedVideo.write_videofile(output_vid)
    st.text("Added translated subtitles and audio to video")
    return output_vid


# Main application logic
def main():
    st.title("TEST")
    # st.title("Foreign Whispers")
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
            fixedText = fix_srt_formatting(translationText)
            fix_srt_encoding(fixedText)
            translationAudio = generate_translation_audio(fixedText, dst)
            output_vid = combine_video_audio_subtitles(video_path, fixedText, translationAudio)

            st.video(output_vid, format="video/mp4", start_time=0)


if __name__ == "__main__":
    main()
