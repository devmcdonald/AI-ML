# Use the official Python base image
FROM python:3.8

# Install ImageMagick
RUN apt-get update && \
    apt-get install -y imagemagick

# Install Streamlit
RUN pip install streamlit

# Copy your Streamlit app and requirements into the Docker image
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the command to run your Streamlit app
CMD ["streamlit", "run", "your_script_name.py"]
