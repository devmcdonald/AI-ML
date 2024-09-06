FROM python:3.9-slim

# Install necessary packages including ffmpeg
RUN apt-get update && apt-get install -y --fix-missing\
    build-essential \
    imagemagick \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

ARG imagemagic_config=/etc/ImageMagick-7.1.1/policy.xml

RUN if [ -f $imagemagic_config ] ; then sed -i 's/<policy domain="path" rights="none" pattern="PDF" \/>/<policy domain="path" rights="read|write" pattern="PDF" \/>/g' $imagemagic_config ; else echo did not see file $imagemagic_config ; fi

# Clone the repository
RUN git clone https://github.com/devmcdonald/AI-ML.git

# Set the working directory
WORKDIR /AI-ML/YouTube_Closed_Captioning_API

# Install Python dependencies
RUN pip install -r requirements.txt -v

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
