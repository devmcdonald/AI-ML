FROM python:3.9-slim

# Install necessary packages including ffmpeg
RUN apt-get update && apt-get install -y --fix-missing\
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

## ImageMagicK Installation 
RUN mkdir -p /tmp/distr && \
    cd /tmp/distr && \
    wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-2.tar.xz && \
    tar xvf ImageMagick-7.0.11-2.tar.xz && \
    cd ImageMagick-7.0.11-2 && \
    ./configure --enable-shared=yes --disable-static --without-perl && \
    make && \
    make install && \
    ldconfig /usr/local/lib && \
    cd /tmp && \
    rm -rf distr

# Clone the repository
RUN git clone https://github.com/devmcdonald/AI-ML.git

# Set the working directory
WORKDIR /AI-ML/YouTube_Closed_Captioning_API

# Install Python dependencies
RUN pip install -r requirements.txt -v

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
