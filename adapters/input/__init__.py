# Input Adapters Package 
from config import WHISPER_MODEL, PYANNOTE_MODEL
from infrastructure.whisper_transcription import WhisperModel
from infrastructure.pyannote_diarization import load_pyannote_pipeline

_whisper_model_instance = None
_pyannote_pipeline_instance = None

def get_whisper_model():
    global _whisper_model_instance
    if _whisper_model_instance is None:
        _whisper_model_instance = WhisperModel(WHISPER_MODEL)
    return _whisper_model_instance

def get_pyannote_pipeline():
    global _pyannote_pipeline_instance
    if _pyannote_pipeline_instance is None:
        _pyannote_pipeline_instance = load_pyannote_pipeline(PYANNOTE_MODEL)
    return _pyannote_pipeline_instance