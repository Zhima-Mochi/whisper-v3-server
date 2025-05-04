from abc import ABC, abstractmethod
from typing import AsyncGenerator
from ..audio_clip import AudioClip

class TranscriptionPort(ABC):
    """
    Port interface for transcription services.
    This defines the contract that any transcription adapter must implement.
    """
    @abstractmethod
    def transcribe(self, clip: AudioClip, start: float, end: float) -> str:
        """
        Transcribe a segment of an audio clip.
        
        Args:
            clip: The audio clip to process
            start: Start time in seconds
            end: End time in seconds
            
        Returns:
            Transcribed text
        """
        pass
        
    @abstractmethod
    async def transcribe_stream(self, clip: AudioClip, start: float, end: float) -> AsyncGenerator[str, None]:
        """
        Stream transcription results as they become available.
        
        Args:
            clip: The audio clip to process
            start: Start time in seconds
            end: End time in seconds
            
        Returns:
            Async generator yielding transcription text as it is processed
        """
        pass 