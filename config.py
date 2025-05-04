import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# App configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))

# PyAnnote and Whisper model configurations
PYANNOTE_MODEL = os.getenv("PYANNOTE_MODEL", "pyannote/speaker-diarization")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "openai/whisper-large-v3")
AUDIO_STORAGE_PATH = os.getenv("AUDIO_STORAGE_PATH", "/tmp/whisper_v3_server_storage")
TRANSCRIPTION_STORAGE_PATH = os.getenv("TRANSCRIPTION_STORAGE_PATH", "/tmp/whisper_v3_server_storage/transcription_texts")
HUGGINGFACE_AUTH_TOKEN = os.getenv("HUGGINGFACE_AUTH_TOKEN")