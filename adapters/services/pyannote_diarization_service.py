import asyncio
from typing import AsyncGenerator, List

from domain.services import DiarizationService
from domain.audio_clip import AudioClip
from domain.speaker_segment import SpeakerSegment
from pyannote.audio import Pipeline

class PyannoteDiarizationService(DiarizationService):
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    async def diarize(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Perform speaker diarization on an audio clip
        
        Raises an exception if the pipeline is not available (None)
        """
        return await self.diarize_async(clip)

    async def diarize_async(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Asynchronously run the pyannote pipeline in a thread pool,
        then collect all segments into a list.
        """
        if self.pipeline is None:
            raise ValueError("Diarization pipeline is not available. See logs for details.")

        loop = asyncio.get_event_loop()
        diarization = await loop.run_in_executor(
            None,
            lambda: self.pipeline({"audio": clip.file_path})
        )

        segments: List[SpeakerSegment] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(
                SpeakerSegment(
                    audio_clip_id=clip.id,
                    start=turn.start,
                    end=turn.end,
                    speaker_label=speaker
                )
            )
        return segments

    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream diarization results: first await the full list,
        then yield one segment at a time.
        """
        segments = await self.diarize_async(clip)
        for seg in segments:
            yield seg 