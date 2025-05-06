import logging
from typing import Dict, Type, Any

# Domain ports
from domain.ports.diarization_port import DiarizationPort
from domain.ports.transcription_port import TranscriptionPort

# Application use cases
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase
from application.use_cases.store_audio_usecase import StoreAudioUseCase

# Outbound adapters
from interfaces.outbound.transcription.whisper_adapter import WhisperAdapter
from interfaces.outbound.transcription.whisper_model import get_whisper_model

from interfaces.outbound.diarization.chunked_diarization_adapter import ChunkedDiarizationAdapter
from interfaces.outbound.diarization.pyannote_model import load_pyannote_pipeline

from interfaces.outbound.repositories.file_system_repository import FileSystemAudioClipRepository
from interfaces.outbound.repositories.file_system_repository import FileSystemTranscriptionTextRepository

# Domain repositories
from domain.repositories import AudioClipRepository, TranscriptionTextRepository

# Configuration
from config import AUDIO_STORAGE_PATH, PYANNOTE_MODEL, TRANSCRIPTION_STORAGE_PATH

logger = logging.getLogger(__name__)

class Container:
    """
    Dependency injection container for the application.
    Follows the composition root pattern in hexagonal architecture.
    """
    def __init__(self):
        # Initialize repositories (outbound adapters)
        logger.info("Pre-initializing audio repository...")
        self._audio_repository = FileSystemAudioClipRepository(AUDIO_STORAGE_PATH)
        logger.info("Audio repository initialized")
        
        logger.info("Pre-initializing transcription repository...")
        self._transcription_repository = FileSystemTranscriptionTextRepository(TRANSCRIPTION_STORAGE_PATH)
        logger.info("Transcription repository initialized")

        # Initialize diarization service (outbound adapter)
        logger.info("Pre-initializing diarization service...")
        pipeline = load_pyannote_pipeline(PYANNOTE_MODEL)
        self._diarization_service = ChunkedDiarizationAdapter(pipeline)
        logger.info("Diarization service initialized")

        # Initialize transcription service (outbound adapter)
        logger.info("Pre-initializing transcription service...")
        whisper_model = get_whisper_model()
        self._transcription_service = WhisperAdapter(whisper_model)
        logger.info("Transcription service initialized")

        # Initialize use cases with their dependencies
        logger.info("Pre-initializing store audio usecase...")
        self._store_audio_usecase = StoreAudioUseCase(self._audio_repository)
        logger.info("Store audio usecase initialized")

        logger.info("Pre-initializing transcribe audio usecase...")
        self._transcribe_audio_usecase = TranscribeAudioUseCase(
            self._diarization_service,
            self._transcription_service,
            self._audio_repository,
            self._transcription_repository
        )
        logger.info("Transcribe audio usecase initialized")

    @property
    def audio_repository(self) -> AudioClipRepository:
        return self._audio_repository

    @property
    def transcription_repository(self) -> TranscriptionTextRepository:
        return self._transcription_repository

    @property
    def diarization_service(self) -> DiarizationPort:
        return self._diarization_service

    @property
    def transcription_service(self) -> TranscriptionPort:
        return self._transcription_service

    @property
    def store_audio_usecase(self) -> StoreAudioUseCase:
        return self._store_audio_usecase

    @property
    def transcribe_audio_usecase(self) -> TranscribeAudioUseCase:
        return self._transcribe_audio_usecase