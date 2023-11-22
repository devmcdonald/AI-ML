import streamlit as st
from transformers import *
from PIL import Image
from pytube import YouTube
import whisper
from whisper.utils import get_writer
import moviepy.editor as mp

#Page title
st.title("Foreign Whispers")

#Youtube link input, download video
link = st.text_input("YouTube URL: ")

#Only continue with input link
if link != '':    
    vid = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    vid.streams.filter(progressive="True").get_highest_resolution().download("/workspaces/Fall-2023-NYU-AI/milestone-5")
    path = "/workspaces/Fall-2023-NYU-AI/milestone-5/" + vid.title + ".mp4"
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
        video = mp.VideoFileClip(path)
        audio = video.audio
        path=path.replace(".mp4", ".mp3")
        audio.write_audiofile(path)
        engAudioFile = path #to reference in future


        #Translate audio files to text (English)
        engModel = whisper.load_model("base")
        result = engModel.transcribe(engAudioFile)
        audio = engAudioFile
        output_directory = "/workspaces/Fall-2023-NYU-AI/milestone-5"
        options = {
                'max_line_width': None,
                'max_line_count': None,
                'highlight_words': False
            }
        txt_writer = get_writer("txt", output_directory)
        txt_writer(result, audio, options)
        engTextFile = output_directory + '/' + title + '.txt' #to reference in future


        #Load pretrained translation model
        task_name = f"translation_{src}_to_{dst}"
        model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"

        translator = pipeline(task_name, model=model_name, tokenizer=model_name)



        #Run inference on each line of input text and write NLP output to new file
        with open(engTextFile, 'r') as f:
            lines = f.readlines()
            translationText=engTextFile.replace(".txt", " translation.txt")
            with open(translationText, 'w') as n:
                for line in lines:
                    n.write(translator(line)[0]["translation_text"] + '\n')
                    
                    


        #Load model for foreign language inference
        model_name = f"tts_models/{dst}/css10/vits"

        #Create output path
        translationAudio=translationText.replace(".txt", ".wav")
            
        # Init TTS with the target model name
        tts = TTS(model_name=model_name, progress_bar=False).to(device)
            
        with open(translationText, 'r') as f:
            #Read text file into string
            txt = f.read()
            #Feed string into model and save output
            tts.tts_to_file(text=txt, file_path=translationAudio)