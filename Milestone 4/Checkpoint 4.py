from TTS.api import TTS
import torch

#Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

#Specify language
lang = "es"

#Load model for inference
model_name = f"tts_models/{lang}/css10/vits"

#Path to translated text files
titles = ["/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Attorney General Merrick Garland The 60 Minutes Interview.txt", 
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Charles Barkley The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Deion Sanders The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Gen Mark Milley The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Godfather of AI Geoffrey Hinton The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of President Joe Biden The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Rich Paul The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Volodymyr Zelenskyy The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of World Number 1 Pool Player Shane Van Boening The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/Milestone 3/Translation of Yannick Nézet-Séguin The 60 Minutes Interview.txt"]


for title in titles:
    #Create output path
    OUTPUT_PATH=title.replace("Milestone 3/Translation of ", "Milestone 4/")
    OUTPUT_PATH=OUTPUT_PATH.replace(".txt", " Audio.wav")
    
    # Init TTS with the target model name
    tts = TTS(model_name=model_name, progress_bar=False).to(device)
    
    with open(title, 'r') as f:
        #Read text file into string
        txt = f.read()
        #Feed string into model and save output
        tts.tts_to_file(text=txt, file_path=OUTPUT_PATH)