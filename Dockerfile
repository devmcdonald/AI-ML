FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --fix-missing\
    build-essential \
    imagemagick \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Modify the ImageMagick policy.xml to allow read and write access to all paths
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@\*"/' /etc/ImageMagick-6/policy.xml || \
    sed -i 's/<policy domain="path" rights="none" pattern="@\*"/<policy domain="path" rights="read|write" pattern="@\*"/' /etc/ImageMagick-7/policy.xml
    
# Clone the repository
RUN git clone https://github.com/devmcdonald/AI-ML.git

# Set the working directory
WORKDIR /AI-ML/YouTube_Closed_Captioning_API

# Install Python dependencies
RUN pip install -r requirements.txt -v

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
