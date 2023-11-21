from transformers import *

#Specify languages - write as variables in final product so user can choose languages
src = "en"
dst = "es"

#Load pretrained model
task_name = f"translation_{src}_to_{dst}"
model_name = f"Helsinki-NLP/opus-mt-{src}-{dst}"

translator = pipeline(task_name, model=model_name, tokenizer=model_name)


titles = ["/workspaces/Fall-2023-NYU-AI/milestone-2/Attorney General Merrick Garland The 60 Minutes Interview.txt", 
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Charles Barkley The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Deion Sanders The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Gen Mark Milley The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Godfather of AI Geoffrey Hinton The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/President Joe Biden The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Rich Paul The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Volodymyr Zelenskyy The 2023 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/World Number 1 Pool Player Shane Van Boening The 60 Minutes Interview.txt",
          "/workspaces/Fall-2023-NYU-AI/milestone-2/Yannick Nézet-Séguin The 60 Minutes Interview.txt"]

#Run inference on each line of input text and write NLP output to new file
for t in titles:
    with open(t, 'r') as f:
        lines = f.readlines()
        t=t.replace("milestone-2/", "milestone-3/Translation of ")
        with open(t, 'w') as n:
            for line in lines:
                n.write(translator(line)[0]["translation_text"] + '\n')