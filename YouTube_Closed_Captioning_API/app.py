import streamlit as st
from transformers import *
from PIL import Image
from pytubefix import YouTube
from pytubefix.cli import on_progress
from pytube.exceptions import VideoUnavailable
import openai
import whisper
from whisper.utils import get_writer, WriteSRT
from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip, AudioFileClip
from moviepy.video.tools.subtitles import SubtitlesClip
import os.path
import time
from TTS.api import TTS
import torch
import re
import sys
import pysrt
from transformers import pipeline
from urllib.error import HTTPError
import os
from moviepy.config import change_settings
import requests
from os import getcwd
import subprocess

# Uncomment for local deployment
#change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

# Uncomment for public deployment
import os
import subprocess
import streamlit as st
from moviepy.config import change_settings

def find_imagemagick():
    # Search common directories and PATH directories
    paths_to_check = [
        "/usr/bin/magick",
        "/usr/local/bin/magick",
        "/bin/magick",
        "/snap/bin/magick",
        "/usr/local/ImageMagick/bin/magick"
    ]
    
    # Add directories from the PATH environment variable
    paths_to_check.extend(os.environ.get("PATH", "").split(os.pathsep))

    # Search for the magick executable in the specified paths
    for path in paths_to_check:
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                if "magick" in files:
                    magick_path = os.path.join(root, "magick")
                    if os.access(magick_path, os.X_OK):
                        return magick_path

    # Fallback: Use the 'which' command to find the path of the magick executable
    result = subprocess.run(["which", "magick"], stdout=subprocess.PIPE)
    path = result.stdout.decode().strip()
    if path:
        return path
    else:
        raise FileNotFoundError("ImageMagick 'magick' executable not found.")

# Step 1: Locate the ImageMagick binary
try:
    imagemagick_path = find_imagemagick()
    st.write(f"ImageMagick binary found at: {imagemagick_path}")

    # Step 2: Update MoviePy configuration
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
    st.success("ImageMagick configuration updated successfully!")

except FileNotFoundError as e:
    st.error(str(e))


# Progress callback function
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    print(f"Download progress: {percentage_of_completion:.2f}%")
    
# Sanitize file name to avoid special characters issues
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

#Page title
st.title("Foreign Whispers")

#Youtube link input, download video
link = ''
link = st.text_input("YouTube URL: ")

# Only continue with input link
if link:
    try:
        # pytubefix version
        vid = YouTube(link, on_progress_callback=on_progress)
        ys = vid.streams.get_highest_resolution()
        sanitized_title = sanitize_filename(vid.title)
        video_path = f"{sanitized_title}.mp4"
        ys.download(filename=video_path)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()  # Stop execution if there's an error in downloading the video

    title = vid.title

    if not os.path.exists(video_path):
        st.error(f"Downloaded video file {video_path} does not exist.")
        st.stop()  # Stop execution if the video file doesn't exist

    # Specify languages 
    src = "en"
    lang = st.selectbox("Target language", ["", "Spanish", "French", "Dutch", "Finnish", "Hungarian"])
    lang_map = {"Spanish": "es", "French": "fr", "Dutch": "nl", "Finnish": "fi", "Hungarian": "hu"}
    dst = lang_map.get(lang, '')

    # Only advance if destination language selected    
    if dst:
        # Separate audio from video file
        video = VideoFileClip(video_path)
        audio = video.audio
        audio_path = f"{sanitized_title}.mp3"
        audio.write_audiofile(audio_path)
        engAudioFile = audio_path  # to reference in future
            
        # Translate audio files to text (English)
        engModel = whisper.load_model("base")
        result = engModel.transcribe(engAudioFile)
            
        # Save transcription as SRT file
        srt_path = f"{sanitized_title}.srt"
        with open(srt_path, 'w') as srt_file:
            for i, segment in enumerate(result["segments"]):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
                srt_file.write(f"{text}\n\n")
            
        engTextFile = srt_path            
                  
        #Load pretrained translation model
        task_name = f"translation_{src}_to_{dst}"
        model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"

        translator = pipeline(task_name, model=model_name, tokenizer=model_name)

        
        #Run inference on each line of input text and write NLP output to new file         
        with open(engTextFile, 'r') as f:
            englishLines = f.read()
            lines = re.split(r'\n\n', englishLines)
            translatedLines = [translator(line)[0]["translation_text"] + '\n' for line in lines]
            
            translationText=engTextFile.replace(".srt", " translation.srt")
            with open(translationText, 'w') as n:
                for line in translatedLines:
                    n.write(line)            
        
        # Fix srt file output (writing as single line)
        with open(translationText, 'r') as file:
            srt_content = file.readlines()

        formatted_subtitles = []

        for entry in srt_content:
            parts = re.split(r'\s+', entry.strip(), maxsplit=4)  # Split into 5 parts using space as delimiter
            if len(parts) == 5:
                sequence_number, time_start, arrow, time_end, text = parts
                time_start = time_start.replace('.', ',')
                time_end = time_end.replace('.', ',')
                formatted_subtitle = f"{sequence_number}\n{time_start} {arrow} {time_end}\n{text}"
                formatted_subtitles.append(formatted_subtitle)

        # Write the corrected subtitles to the file
        fixedText = translationText.replace("translation.srt", "fixed translation.srt")
        with open(fixedText, 'w') as file:
            file.writelines('\n\n'.join(formatted_subtitles))
                    
        with open(fixedText, 'r') as file:
            lines = file.readlines()
        lines = lines[:-3]
        with open(fixedText, 'w') as file:
            file.writelines(lines)      
        
        
        
        fixedText = translationText.replace("translation.srt", "fixed translation.srt")
        #Get device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        #Load model for foreign language inference
        model_name = f"tts_models/{dst}/css10/vits"

        #Create output path
        translationAudio=fixedText.replace(".srt", ".mp3")
            
        # Init TTS with the target model name
        tts = TTS(model_name=model_name, progress_bar=False).to(device)
            
        with open(translationText, 'r') as f:
            #Read text file into string
            txt = f.read()
            #Feed string into model and save output
            tts.tts_to_file(text=txt, file_path=translationAudio)
        
 
        
        
        
        
        fixedText = f"{title} fixed translation.srt"
        fixedText = fixedText.replace(":", "")
        
        translatedAudio = fixedText.replace(".srt", ".mp3")
        #Add translated subtitles to video
        output_vid = "output_vid.mp4"
        try:
            with open(fixedText, 'r', encoding='utf-8', errors='replace') as file:
                sub_content = file.read()
        except UnicodeDecodeError:
            try:
                with open(fixedText, 'r', encoding='ISO-8859-1') as file:
                    sub_content = file.read()
            except UnicodeDecodeError:
                with open(fixedText, 'r', encoding='cp1252', errors='replace') as file:
                    sub_content = file.read()
            
        generator = lambda txt: TextClip(txt, font='Arial', fontsize=28, color='white')
        subs = SubtitlesClip(fixedText, generator) 
        result = CompositeVideoClip([video, subs.set_position(("center", "bottom"))])

        
        # Replace audio of video
        audio = AudioFileClip(translatedAudio)
        translatedVideo = result.set_audio(audio)
        translatedVideo.write_videofile(output_vid)
        
        # Upload final video to streamlit
        st.video(output_vid, format="video/mp4", start_time=0) 

        
      
            
        