from pytube import YouTube

links = ["https://www.youtube.com/watch?v=d403nALfQrE",
         "https://www.youtube.com/watch?v=OA2Tj75T3fI",
         "https://www.youtube.com/watch?v=qrvK_KuIeJk",
         "https://www.youtube.com/watch?v=oFVuQ0RP_As",
         "https://www.youtube.com/watch?v=4aPp8KX6EiU",
         "https://www.youtube.com/watch?v=h8PSWeRLGXs",
         "https://www.youtube.com/watch?v=Z8qC2tVkGeU",
         "https://www.youtube.com/watch?v=ervLwxz7xPo",
         "https://www.youtube.com/watch?v=_e0Ez7bO1is",
         "https://www.youtube.com/watch?v=YBY-CdpH0CA"]

for l in links:
    vid = YouTube(l)
    vid.streams.filter(progressive="True").get_highest_resolution().download("/workspaces/Fall-2023-NYU-AI/milestone-1")
    

