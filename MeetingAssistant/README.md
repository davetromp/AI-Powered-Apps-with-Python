# 🎙️ Meeting Assistant

A Python application that transcribes meeting audio recordings and generates concise summaries using AI.

## Features

- ✅ **Audio Transcription**: Uses OpenAI's Whisper model for accurate speech-to-text
- ✅ **AI-Powered Summary**: Generates meeting summaries using Ollama (gemma3:latest)
- ✅ **Configurable Summary Length**: Choose between brief, detailed, or very brief summaries
- ✅ **Real-time Progress**: Track transcription and summarization progress
- ✅ **Download Outputs**: Save transcripts and summaries as text files
- ✅ **Multiple Audio Formats**: Supports WAV, MP3, M4A, FLAC, OGG, and WMA
- ✅ **Gradio Interface**: Clean, user-friendly web interface

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running
- gemma3:latest model downloaded in Ollama

## Installation

### 1. Clone or navigate to the project directory

```bash
cd /path/to/MeetingAssistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Ollama is running

Make sure Ollama is installed and the gemma3:latest model is available:

```bash
# Check if Ollama is running
ollama list

# If gemma3:latest is not installed, download it:
ollama pull gemma3:latest
```

## Usage

### Start the application

```bash
python app.py
```

The application will start and be available at `http://localhost:7860`

### Using the interface

1. **Upload Audio**: Click "Upload Meeting Audio" to select an audio file or record directly via microphone
2. **Configure Summary**: Select your preferred summary length (brief, detailed, or very brief)
3. **Process**: Click "Transcribe and Summarize" to begin processing
4. **View Results**: Both the transcription and summary will appear in the respective text boxes
5. **Download**: Use the download buttons to save the transcription and/or summary as text files

## Configuration

You can customize the application settings in `config.py`:

- `WHISPER_MODEL`: Whisper model size (tiny, base, small, medium, large)
- `OLLAMA_MODEL`: Ollama model name
- `MAX_AUDIO_SIZE_MB`: Maximum audio file size in MB
- `SUMMARY_LENGTH_OPTIONS`: Customize summary instructions

## Project Structure

```
MeetingAssistant/
├── app.py              # Main Gradio application
├── config.py           # Configuration settings
├── transcriber.py      # Whisper transcription logic
├── summarizer.py       # Ollama summarization logic
├── utils.py            # Helper functions
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Troubleshooting

### Ollama connection issues

- Ensure Ollama is running: `ollama serve`
- Check that the gemma3:latest model is installed: `ollama list`
- Verify the API is accessible at `http://localhost:11434`

### Whisper model issues

- The Whisper model will be downloaded automatically on first run
- Ensure you have sufficient disk space (~150MB for base model)
- For better performance, consider using a larger Whisper model (small, medium, large)

### Import errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Ensure your virtual environment is activated

## License

This project is open source and available for educational purposes.