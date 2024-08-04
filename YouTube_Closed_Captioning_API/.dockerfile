# Use the official Streamlit base image
FROM streamlit/streamlit:latest

# Install ImageMagick
RUN apt-get update && \
    apt-get install -y imagemagick

# Copy your Streamlit app into the Docker image
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Set the command to run your Streamlit app
CMD ["streamlit", "run", "app.py"]
