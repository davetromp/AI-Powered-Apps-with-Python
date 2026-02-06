import os
from pathlib import Path
from typing import Tuple, Optional
from config import Config


def validate_audio_file(file_path: str) -> Tuple[bool, Optional[str]]:
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in Config.SUPPORTED_AUDIO_FORMATS:
        return False, f"Unsupported file format. Supported formats: {', '.join(Config.SUPPORTED_AUDIO_FORMATS)}"
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > Config.MAX_AUDIO_SIZE_MB:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({Config.MAX_AUDIO_SIZE_MB} MB)"
    
    return True, None


def format_transcription_info(result: dict) -> str:
    text = result.get("text", "")
    language = result.get("language", "unknown")
    duration = result.get("duration", 0)
    
    info_lines = [
        f"Transcription completed successfully!",
        f"Language detected: {language}",
        f"Audio duration: {duration:.1f} seconds",
        "-" * 50,
        "\nTranscription:\n",
        text
    ]
    
    return "\n".join(info_lines)


def save_to_file(content: str, filename: str, output_dir: str = "outputs") -> str:
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return file_path


def get_safe_filename(original_name: str, prefix: str = "") -> str:
    name = Path(original_name).stem
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    
    if prefix:
        safe_name = f"{prefix}_{safe_name}"
    
    return f"{safe_name}.txt"