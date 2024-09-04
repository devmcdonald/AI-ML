FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    imagemagick \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository
RUN git clone https://github.com/devmcdonald/AI-ML.git

# Set the working directory
WORKDIR /AI-ML/YouTube_Closed_Captioning_API

RUN pip install -r requirements.txt -v

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]