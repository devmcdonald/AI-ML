import whisper
from whisper.utils import get_writer
import moviepy.editor as mp


#Separate audio from video mp4 files
titles = ["/workspaces/Fall-2023-NYU-AI/Milestone 1/Attorney General Merrick Garland The 60 Minutes Interview.mp4", 
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Charles Barkley The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Deion Sanders The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Gen Mark Milley The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Godfather of AI Geoffrey Hinton The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/President Joe Biden The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Rich Paul The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Volodymyr Zelenskyy The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/World Number 1 Pool Player Shane Van Boening The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Milestone 1/Yannick Nézet-Séguin The 60 Minutes Interview.mp4"]
for t in titles:
    video = mp.VideoFileClip(t)
    audio = video.audio
    t=t.replace("Milestone 1", "Milestone 2")
    t=t.replace(".mp4", ".mp3")
    audio.write_audiofile(t)

#Translate audio files to text (English)
for t in titles:
    t=t.replace("Milestone 1", "Milestone 2")
    t=t.replace(".mp4", ".mp3")
    model = whisper.load_model("base")
    result = model.transcribe(t)
    audio = t
    t=t.replace("/workspaces/Fall-2023-NYU-AI/Milestone 2/", "")
    t=t.replace(".mp3", "")
    output_directory = "/workspaces/Fall-2023-NYU-AI/Milestone 2"
    options = {
        'max_line_width': None,
        'max_line_count': None,
        'highlight_words': False
    }
    txt_writer = get_writer("txt", output_directory)
    txt_writer(result, audio, options)