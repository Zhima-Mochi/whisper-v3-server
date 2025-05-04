from typing import AsyncGenerator, List
import asyncio
from uuid import UUID

from domain.ports.diarization_port import DiarizationPort
from domain.audio_clip import AudioClip
from domain.speaker_segment import SpeakerSegment

class FakeDiarizationService(DiarizationPort):
    """
    Fake implementation of the DiarizationPort for testing purposes.
    Returns predefined speaker segments without actual audio processing.
    """
    
    def __init__(self, 
                 segment_duration: float = 5.0, 
                 total_duration: float = 30.0,
                 num_speakers: int = 2):
        """
        Initialize the fake diarization service.
        
        Args:
            segment_duration: Duration of each segment in seconds
            total_duration: Total duration of the audio in seconds
            num_speakers: Number of unique speakers to generate
        """
        self.segment_duration = segment_duration
        self.total_duration = total_duration
        self.num_speakers = num_speakers
    
    async def diarize(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Return predefined speaker segments.
        
        Args:
            clip: The audio clip to process (ignored in fake implementation)
            
        Returns:
            List of speaker segments with timing information
        """
        return [segment async for segment in self.diarize_stream(clip)]
    
    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream fake speaker segments.
        
        Args:
            clip: The audio clip to process (ignored in fake implementation)
            
        Returns:
            Async generator yielding speaker segments
        """
        current_time = 0.0
        
        while current_time < self.total_duration:
            end_time = min(current_time + self.segment_duration, self.total_duration)
            speaker_idx = int(current_time / self.segment_duration) % self.num_speakers
            
            segment = SpeakerSegment(
                audio_clip_id=clip.id,
                start=current_time,
                end=end_time,
                speaker_label=f"SPEAKER_{speaker_idx + 1}"
            )
            
            # Simulate some processing time
            await asyncio.sleep(0.05)
            
            yield segment
            current_time = end_time 