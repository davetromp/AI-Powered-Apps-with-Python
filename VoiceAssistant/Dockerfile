FROM python:3.13

WORKDIR /app
COPY . .

# install zstd for ollama, espeak for basic tts and ffmpeg for stt
RUN apt update
RUN apt -y install zstd espeak-ng libespeak1 ffmpeg

# install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh
RUN ollama serve 
# RUN systemctl enable ollama
# RUN systemctl start ollama
RUN ollama pull llama3.2:1b

# install the needed python libraries
RUN pip install -r requirements.txt

# Set the environment variable HF_TOKEN
ENV HF_TOKEN="YOUR TOKEN FROM HuggingFace"

CMD ["python", "-u", "server.py"]