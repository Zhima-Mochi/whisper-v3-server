import asyncio
from typing import AsyncGenerator, List

from domain.ports.diarization_port import DiarizationPort
from domain.audio_clip import AudioClip
from domain.speaker_segment import SpeakerSegment
from pyannote.audio import Pipeline

class PyannoteDiarizationService(DiarizationPort):
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        
    async def diarize(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Diarize the audio clip and return a list of speaker segments.
        """
        segments = [seg async for seg in self.diarize_stream(clip)]
        return segments

    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream speaker segments as soon as they are available.
        Uses a background thread to run the full pipeline, pushing each segment
        into an asyncio.Queue, which this async generator then yields from.
        """
        if not self.pipeline:
            raise ValueError("Diarization pipeline is not available")

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def worker():
            # run full pipeline in thread
            diarization = self.pipeline({"audio": clip.file_path})
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segment = SpeakerSegment(
                    audio_clip_id=clip.id,
                    start=turn.start,
                    end=turn.end,
                    speaker_label=speaker
                )
                loop.call_soon_threadsafe(queue.put_nowait, segment)
            # signal completion
            loop.call_soon_threadsafe(queue.put_nowait, None)

        loop.run_in_executor(None, worker)

        # yield segments as they arrive
        while True:
            seg = await queue.get()
            if seg is None:
                break
            yield seg
