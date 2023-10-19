import whisper
import moviepy.editor as mp


#Separate audio from video mp4 files

titles = ["/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Attorney General Merrick Garland The 60 Minutes Interview.mp4", 
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Charles Barkley The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Deion Sanders The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Gen Mark Milley The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Godfather of AI Geoffrey Hinton The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/President Joe Biden The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Rich Paul The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Volodymyr Zelenskyy The 2023 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/World Number 1 Pool Player Shane Van Boening The 60 Minutes Interview.mp4",
          "/workspaces/Fall-2023-NYU-AI/Project Checkpoint 1/Yannick Nézet-Séguin The 60 Minutes Interview.mp4"]
for t in titles:
    video = mp.VideoFileClip(t)
    audio = video.audio
    t=t.replace("Project Checkpoint 1", "Project Checkpoint 2")
    t=t.replace(".mp4", ".mp3")
    audio.write_audiofile(t)

#Translate audio files to text (English)
for t in titles:
    t=t.replace("Project Checkpoint 1", "Project Checkpoint 2")
    t=t.replace(".mp4", ".mp3")
    model = whisper.load_model("base")
    result = model.transcribe(t)
    t=t.replace("/workspaces/Fall-2023-NYU-AI/Project Checkpoint 2/", "")
    t=t.replace(".mp3", ".txt")
    with open("/workspaces/Fall-2023-NYU-AI/Project Checkpoint 2/Whisper " + t, "w", encoding="utf-8") as txt:
        txt.write(result["text"])
