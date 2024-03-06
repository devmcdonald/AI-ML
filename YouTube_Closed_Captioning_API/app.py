import streamlit as st
from transformers import *
from PIL import Image
from pytube import YouTube
import openai
import whisper
from whisper.utils import get_writer
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

#Page title
st.title("Foreign Whispers")

#Youtube link input, download video
link = ''
link = st.text_input("YouTube URL: ")

#Only continue with input link
if link != '':    
    vid = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    vid.streams.filter(progressive="True").get_highest_resolution().download("/workspaces/AI-&-ML/YouTube_Closed_Captioning_API")
    path = "/workspaces/AI-&-ML/YouTube_Closed_Captioning_API/" + vid.title + ".mp4"
    title = vid.title

    #Specify languages 
    src = "en"
    lang = st.selectbox("Target language", ["", "Spanish", "French", "Dutch", "Finnish", "Hungarian"])
    if lang == "Spanish":
        dst = "es"
    elif lang == "French":
        dst = "fr"
    elif lang == "Dutch":
        dst = "nl"
    elif lang == "Finnish":
        dst = "fi"
    elif lang == "Hungarian":
        dst = "hu"
    else:
        dst = ''
        
    #Only advance if destination language selected    
    if dst != '':
        #Separate audio from video file
        path = path.replace(":", "")
        video = VideoFileClip(path)
        audio = video.audio
        path=path.replace(".mp4", ".mp3")
        audio.write_audiofile(path)
        engAudioFile = path #to reference in future

    
        #Translate audio files to text (English)
        engModel = whisper.load_model("base")
        result = engModel.transcribe(engAudioFile)
        
        audio = engAudioFile
        output_directory = "/workspaces/AI-&-ML/YouTube_Closed_Captioning_API"
        
        srt_writer = get_writer("srt", output_directory)
        srt_writer(result, audio)
    
        output_directory = "/workspaces/AI-&-ML/YouTube_Closed_Captioning_API"  
        engTextFile = output_directory + '/' + title + '.srt' #to reference in future
        engTextFile=engTextFile.replace(":", "")

        translationText=engTextFile.replace(".srt", " translation.srt")
        

          
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
        
 
        
        
        
        
        fixedText = f"/workspaces/AI-&-ML/YouTube_Closed_Captioning_API/{title} fixed translation.srt"
        fixedText = fixedText.replace(":", "")
        
        translatedAudio = fixedText.replace(".srt", ".mp3")
        #Add translated subtitles to video
        output_vid = "/workspaces/AI-&-ML/YouTube_Closed_Captioning_API/output_vid.mp4"
        with open(fixedText, 'r', encoding='utf-8') as file:
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
        
        
      
            
        