from abc import ABC, abstractmethod
from .audio_clip import AudioClip
from .speaker_segment import SpeakerSegment

class DiarizationService(ABC):
    @abstractmethod
    def diarize(self, clip: AudioClip) -> list[SpeakerSegment]:
        pass

class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, clip: AudioClip, start: float, end: float) -> str:
        pass 