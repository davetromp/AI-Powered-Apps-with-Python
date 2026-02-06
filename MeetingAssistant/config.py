import os

class Config:
    WHISPER_MODEL = "base"
    WHISPER_DEVICE = "cpu"
    
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL = "glm-4.7:cloud"
    OLLAMA_TIMEOUT = 300
    
    MAX_AUDIO_SIZE_MB = 100
    SUPPORTED_AUDIO_FORMATS = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".wma"]
    
    SUMMARY_LENGTH_OPTIONS = {
        "brief": "Provide a concise summary in 2-3 paragraphs.",
        "detailed": "Provide a comprehensive summary with all key details.",
        "very_brief": "Provide an extremely brief summary in 1 paragraph."
    }
    DEFAULT_SUMMARY_LENGTH = "brief"
    
    SUMMARY_PROMPT_TEMPLATE = """You are a professional meeting assistant. Please summarize the following meeting transcription.

{length_instruction}

Focus on:
- Key topics discussed
- Important decisions made
- Action items and responsibilities

Meeting Transcription:
{transcription}"""