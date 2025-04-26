from abc import ABC, abstractmethod
from .audio_clip import AudioClip
from .speaker_segment import SpeakerSegment
from .transcription_text import TranscriptionText

class AudioClipRepository(ABC):
    @abstractmethod
    def save(self, clip: AudioClip):
        pass

    @abstractmethod
    def get(self, clip_id):
        pass

    @abstractmethod
    def delete(self, clip_id):
        pass

class SpeakerSegmentRepository(ABC):
    @abstractmethod
    def save(self, clip_id: str, segments: list[SpeakerSegment]):
        pass

    @abstractmethod
    def list(self, clip_id):
        pass

    @abstractmethod
    def delete(self, clip_id):
        pass

class TranscriptionTextRepository(ABC):
    @abstractmethod
    def save(self, clip_id: str, texts: list[TranscriptionText]):
        pass

    @abstractmethod
    def list(self, clip_id):
        pass 

    @abstractmethod
    def delete(self, clip_id):
        pass