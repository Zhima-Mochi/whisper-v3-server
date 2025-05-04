from typing import Dict, Type, Any
from domain.ports.diarization_port import DiarizationPort
from domain.ports.transcription_port import TranscriptionPort
from adapters.services.chunked_diarization_service import ChunkedDiarizationService
from adapters.services.fake_diarization_service import FakeDiarizationService
from adapters.services.whisper_transcription_service import WhisperTranscriptionService
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase
from infrastructure.whisper_transcription import get_whisper_model
from infrastructure.pyannote_diarization import load_pyannote_pipeline
from infrastructure.repositories.audio_repository_impl import FileSystemAudioClipRepositoryImpl
from infrastructure.repositories.transcription_repository_impl import FileSystemTranscriptionTextRepositoryImpl
from config import AUDIO_STORAGE_PATH, PYANNOTE_MODEL, TRANSCRIPTION_STORAGE_PATH
from domain.repositories import *

class DIContainer:
    """
    Dependency Injection Container for managing service instances.
    Provides a central place to create and access implementations of ports.
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._testing_mode = False

        # Static services (no need to delay)
        self._services[TranscriptionTextRepository] = FileSystemTranscriptionTextRepositoryImpl(TRANSCRIPTION_STORAGE_PATH)
        self._services[AudioClipRepository] = FileSystemAudioClipRepositoryImpl(AUDIO_STORAGE_PATH) 
    
    def set_testing_mode(self, is_testing: bool):
        """
        Enable or disable testing mode. When testing is enabled,
        fake implementations will be used instead of real ones.
        """
        self._testing_mode = is_testing
        if is_testing:
            self._services = {}
        else:
            self._services[TranscriptionTextRepository] = FileSystemTranscriptionTextRepositoryImpl(TRANSCRIPTION_STORAGE_PATH)
            self._services[AudioClipRepository] = FileSystemAudioClipRepositoryImpl(AUDIO_STORAGE_PATH)

    def get_diarization_service(self) -> DiarizationPort:
        """
        Get an implementation of the DiarizationPort.
        Returns FakeDiarizationService in testing mode,
        or ChunkedDiarizationService in normal mode.
        """
        if self._testing_mode:
            return FakeDiarizationService()
        if DiarizationPort not in self._services:
            pipeline = load_pyannote_pipeline(PYANNOTE_MODEL)
            self._services[DiarizationPort] = ChunkedDiarizationService(pipeline)
        return self._services[DiarizationPort]
    
    def get_transcription_service(self) -> TranscriptionPort:
        """
        Get an implementation of the TranscriptionPort.
        """
        if TranscriptionPort not in self._services:
            self._services[TranscriptionPort] = WhisperTranscriptionService(get_whisper_model())
        return self._services[TranscriptionPort]
    
    def get_transcribe_use_case(self) -> TranscribeAudioUseCase:
        """
        Get an instance of the TranscribeAudioUseCase with all dependencies injected.
        """
        return TranscribeAudioUseCase(
            diarization_service=self.get_diarization_service(),
            transcription_service=self.get_transcription_service(),
            audio_repository=self.get_audio_repository(),
            transcription_repository=self.get_transcription_repository()
        )

    def get_audio_repository(self):
        """
        Get an implementation of the AudioClipRepository.
        """
        return self._services[AudioClipRepository]
    
    def get_transcription_repository(self):
        """
        Get an implementation of the TranscriptionTextRepository.
        """
        return self._services[TranscriptionTextRepository]

# Singleton instance
container = DIContainer() 