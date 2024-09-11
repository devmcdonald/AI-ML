# Foreign Whispers

## Sections
- [About](#about)
- [Example Outputs](#example-outputs)
- [How to Use](#how-to-use)
- [Recommendations](#recommendations)


## About
Foreign Whispers is a tool designed to transform your video content by adding both spoken and written subtitles in your language of choice, all while replicating the original voices. This powerful application harnesses cutting-edge AI technologies to provide a seamless and engaging viewing experience for diverse audiences.

### Features:
- **YouTube Video Download:** Automatically downloads YouTube videos to use as input for subtitle and voice replication, making the process straightforward and efficient.
- **Voice Cloning and Translation:** Clones voices and translates spoken content into your desired language, making your content accessible to many audiences.
- **Video Compilation:** Integrates the translated audio and subtitles into the original video. This process ensures that the final output maintains the video’s original flow and visual coherence while incorporating the new language features.
- **Audio Stretching/Shrinking:** To match the video length, the script speeds up the audio in specific sections. This ensures that the translated speech fits within the given timestamps for each speaker's segment.

### Issues:
- **Audio Speed:** Adjusting audio speed can result in unnatural sound, making it hard to understand.
- **Audio Artifacts:** Background noise and model variability can introduce random audio artifacts, affecting the clarity and quality of the output.

## Example

- **Input Video:**  
  [Click here to view the input video](https://github.com/devmcdonald/AI-ML/blob/73d5a5a0da49d642677ec95cdd28c860856c9159/YouTube_Closed_Captioning_API/Novak%20Djokovic%20The%2060%20Minutes%20Interview.mp4)



- **Output:**  
  [Click here to view the output video](https://github.com/devmcdonald/AI-ML/blob/73d5a5a0da49d642677ec95cdd28c860856c9159/YouTube_Closed_Captioning_API/output_vid.mp4)



## How to Use
Before running the script, ensure you have Python installed on your machine. You can download Python from the [official website](https://www.python.org/downloads/).

1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/devmcdonald/AI-ML.git
    ```
2. Navigate to the project directory and start a virtual environment:
    ```bash
    cd YouTube_Closed_Captioning_API
    virtualenv venv
    venv/Scripts/activate
    ```
3. Install the requirements necessary:
    ```
    pip install -r requirements.txt
    ```
4. Spin up the app with this command:
    ```
    streamlit run app.py
    ```
5. The app will open in a browser. Input your URL link for your desired YouTube video and the language you'd like it translated into. 

*Note: The time required for the script to complete depends on the computational power of your GPU.*

6. This script works best with a GPU for acceleration. You need to have a GPU with CUDA support and the appropriate CUDA toolkit installed. Follow the [CUDA installation guide](https://developer.nvidia.com/cuda-toolkit) for details.



## Recommendation
This application works best when cloning the repository and running locally on your own hardware for optimal performance and faster processing. This application should not be deployed publicly due to API constraints. 
