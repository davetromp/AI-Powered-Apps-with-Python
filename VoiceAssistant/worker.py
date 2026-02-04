import requests
import os, time
from ollama import chat, generate
from ollama import ChatResponse
from dotenv import load_dotenv, dotenv_values 
import pyttsx3
import whisper
from transformers import AutoProcessor, BarkModel
import scipy
from TTS.api import TTS

# loading variables from .env file
# Stor your HF_TOKEN from HuggingFace for faster downloads of models.
load_dotenv()


def preload_models():
    """Preload Whisper and Coqui TTS models into memory for faster inference."""
    whisper.load_model("base")
    TTS(model_name="tts_models/eng/fairseq/vits").to("cpu")


def speech_to_text(audio_binary):
    """Convert audio binary data to text using OpenAI Whisper model.

    Args:
        audio_binary: Binary audio data (e.g., WAV format)

    Returns:
        str: Transcribed text from the audio
    """
    print("Whisper STT")
    # setting the model
    sttmodel = whisper.load_model("base")
    with open("audio.wav", 'wb') as audiofile:
        audiofile.write(audio_binary)
    result = sttmodel.transcribe('audio.wav')
    return result["text"] 


def basic_text_to_speech(response_text):
    """Convert text to speech using pyttsx3 (basic offline TTS engine).

    Args:
        response_text: Text to convert to speech

    Returns:
        bytes: Binary WAV audio data of the synthesized speech
    """
    print("Basic TTS")
    basic_tts_engine = pyttsx3.init()             # Initiate the engine
    basic_tts_engine.setProperty('rate', 100)     # setting up new voice rate
    basic_tts_engine.setProperty('pitch', -200)     # lowering the pitch
    # default voice = en -- very robotic on linux while using espeak
    try:
        basic_tts_engine.setProperty('voice', 'mb-us2') # install mbrola-us2 to use mb-us2 for slightly better voice
    except:
        basic_tts_engine.setProperty('voice', 'en') # default British english voice
    basic_tts_engine.save_to_file(response_text, "response.wav") 
    basic_tts_engine.runAndWait()
    time.sleep(3)
    # read in the response.wav file as audio_binary
    with open("response.wav", 'rb') as audio_binary:
        speech_response = audio_binary.read()
    os.remove("response.wav")
    return speech_response


def bark_text_to_speech(text):
    """Convert text to speech using Suno Bark TTS model (high quality neural TTS).

    Args:
        text: Text to convert to speech

    Returns:
        bytes: Binary WAV audio data of the synthesized speech

    Note:
        Requires HF_TOKEN environment variable for model download from HuggingFace
    """
    print("Bark TTS")
    token = os.getenv('HF_TOKEN')
    bark_processor = AutoProcessor.from_pretrained("suno/bark-small", token=token)
    bark_model = BarkModel.from_pretrained("suno/bark-small", token=token)
    print("Done loading models")

    voice_preset = "v2/en_speaker_6"
    inputs = bark_processor(text, voice_preset=voice_preset)
    audio_array = bark_model.generate(**inputs)
    audio_array = audio_array.cpu().numpy().squeeze()

    sample_rate = bark_model.generation_config.sample_rate
    scipy.io.wavfile.write("response.wav", rate=sample_rate, data=audio_array)

    with open("response.wav", 'rb') as audio_binary:
        speech_response = audio_binary.read()
    os.remove("response.wav")
    return speech_response


def coqui_text_to_speech(text):
    """Convert text to speech using Coqui TTS VITS model.

    Args:
        text: Text to convert to speech

    Returns:
        bytes: Binary WAV audio data of the synthesized speech
    """
    api = TTS(model_name="tts_models/eng/fairseq/vits").to("cpu")
    api.tts_to_file(text, file_path="response.wav")
    with open("response.wav", 'rb') as audio_binary:
        speech_response = audio_binary.read()
    os.remove("response.wav")
    return speech_response    
    

def text_to_speech(text, voice='basic'):
    """Convert text to speech using specified TTS engine.

    Args:
        text: Text to convert to speech
        voice: TTS engine to use - 'basic' (pyttsx3), 'coqui', or 'bark'

    Returns:
        bytes: Binary WAV audio data of the synthesized speech
    """
    if voice=='basic' or voice=='default':
        return basic_text_to_speech(text)
    elif voice=='coqui':
        return coqui_text_to_speech(text)
    elif voice=='bark':
        return bark_text_to_speech(text)


messages = []
def ollama_process_message(user_message):
    """Process user message using Ollama Llama 3.2 1B model with conversation history.

    Args:
        user_message: User's text message to process

    Returns:
        str: The chatbot's text response

    Note:
        Maintains conversation history in the global 'messages' list
    """
    message =  {
        'role': 'user', 
        'content': user_message,
    }
    messages.append(message)
    response: ChatResponse = chat(model='llama3.2:1b', messages=messages)
    response_text = response.message.content
    response_message = {
        'role': 'chatbot', 
        'content': response_text,
    }
    messages.append(response_message)
    return response_text