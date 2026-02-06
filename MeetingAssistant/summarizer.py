import requests
from typing import Callable, Optional
from config import Config


class Summarizer:
    def __init__(self, base_url=None, model=None):
        self.base_url = base_url or Config.OLLAMA_BASE_URL
        self.model = model or Config.OLLAMA_MODEL
        self.timeout = Config.OLLAMA_TIMEOUT
    
    def _call_ollama_api(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 2048
            }
        }
        
        response = requests.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    def summarize(
        self,
        transcription: str,
        summary_length: str = "brief",
        progress: Optional[Callable] = None
    ) -> str:
        if not transcription or not transcription.strip():
            return "No transcription provided to summarize."
        
        if progress:
            progress(0.5, desc="Generating summary with Ollama...")
        
        length_instruction = Config.SUMMARY_LENGTH_OPTIONS.get(
            summary_length,
            Config.SUMMARY_LENGTH_OPTIONS[Config.DEFAULT_SUMMARY_LENGTH]
        )
        
        prompt = Config.SUMMARY_PROMPT_TEMPLATE.format(
            length_instruction=length_instruction,
            transcription=transcription
        )
        
        try:
            summary = self._call_ollama_api(prompt)
            
            if progress:
                progress(1.0, desc="Summary generated successfully")
            
            return summary
        except requests.exceptions.RequestException as e:
            error_msg = f"Error calling Ollama API: {str(e)}"
            if progress:
                progress(1.0, desc=error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error during summarization: {str(e)}"
            if progress:
                progress(1.0, desc=error_msg)
            return error_msg