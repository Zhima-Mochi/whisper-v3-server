from abc import ABC, abstractmethod
from typing import AsyncGenerator, List
from ..audio_clip import AudioClip
from ..speaker_segment import SpeakerSegment

class DiarizationPort(ABC):
    """
    Port interface for speaker diarization services.
    This defines the contract that any diarization adapter must implement.
    """
    @abstractmethod
    async def diarize(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Diarize an audio clip and return speaker segments.
        
        Args:
            clip: The audio clip to process
            
        Returns:
            List of speaker segments with timing information
        """
        pass
        
    @abstractmethod
    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream speaker segments as they become available.
        
        Args:
            clip: The audio clip to process
            
        Returns:
            Async generator yielding speaker segments as they are processed
        """
        pass 