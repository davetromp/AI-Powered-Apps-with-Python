import whisper
from typing import Generator, Dict, Any
from config import Config


class Transcriber:
    def __init__(self, model_name=None, device=None):
        self.model_name = model_name or Config.WHISPER_MODEL
        self.device = device or Config.WHISPER_DEVICE
        self.model = None
    
    def load_model(self, progress=None):
        if self.model is None:
            if progress:
                progress(0.1, desc="Loading Whisper model...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            if progress:
                progress(0.2, desc="Whisper model loaded")
    
    def transcribe(self, audio_path: str, progress=None) -> Generator[Dict[str, Any], None, None]:
        self.load_model(progress)
        
        if progress:
            progress(0.3, desc="Loading audio file...")
        
        audio = whisper.load_audio(audio_path)
        
        if progress:
            progress(0.5, desc="Starting transcription...")
        
        result = self.model.transcribe(
            audio,
            language=None,
            task="transcribe",
            word_timestamps=False,
            fp16=False
        )
        
        if progress:
            progress(1.0, desc="Transcription complete")
        
        yield {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "duration": len(audio) / whisper.audio.SAMPLE_RATE
        }
    
    def transcribe_sync(self, audio_path: str, progress=None) -> Dict[str, Any]:
        for result in self.transcribe(audio_path, progress):
            return result
        return {}