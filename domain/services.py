from abc import ABC, abstractmethod
from typing import AsyncGenerator
from .audio_clip import AudioClip
from .speaker_segment import SpeakerSegment

class DiarizationService(ABC):
    @abstractmethod
    def diarize(self, clip: AudioClip) -> list[SpeakerSegment]:
        pass
        
    @abstractmethod
    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        pass

class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, clip: AudioClip, start: float, end: float) -> str:
        pass
        
    @abstractmethod
    async def transcribe_stream(self, clip: AudioClip, start: float, end: float) -> AsyncGenerator[str, None]:
        pass 