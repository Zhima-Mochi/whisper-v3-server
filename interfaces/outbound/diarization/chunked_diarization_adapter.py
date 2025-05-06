import os
import asyncio
import tempfile
from typing import AsyncGenerator, List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from pydub import AudioSegment, silence
from pyannote.audio import Pipeline

from domain.ports.diarization_port import DiarizationPort
from domain.audio_clip import AudioClip
from domain.speaker_segment import SpeakerSegment

def detect_chunks(
    file_path: str,
    min_silence_ms: int = 600,
    silence_thresh_db: int = -40,
    min_chunk_duration: float = 0.5  # Minimum chunk duration in seconds
) -> List[Tuple[float, float]]:
    """
    Detect chunks in audio file based on silence detection.
    Returns a list of (start_sec, end_sec) tuples.
    
    Args:
        file_path: Path to the audio file
        min_silence_ms: Minimum silence duration in milliseconds
        silence_thresh_db: Silence threshold in dB
        min_chunk_duration: Minimum chunk duration in seconds
    """
    audio = AudioSegment.from_file(file_path)
    silent_ranges = silence.detect_silence(
        audio,
        min_silence_len=min_silence_ms,
        silence_thresh=silence_thresh_db
    )
    
    segments, prev_end = [], 0
    for start_ms, end_ms in silent_ranges:
        if prev_end < start_ms:
            chunk_duration = (start_ms - prev_end) / 1000.0
            if chunk_duration >= min_chunk_duration:
                segments.append((prev_end/1000.0, start_ms/1000.0))
        prev_end = end_ms
    
    # Add the last segment if it's long enough
    if prev_end < len(audio):
        last_duration = (len(audio) - prev_end) / 1000.0
        if last_duration >= min_chunk_duration:
            segments.append((prev_end/1000.0, len(audio)/1000.0))
    
    return segments

class ChunkedDiarizationAdapter(DiarizationPort):
    """
    Adapter implementation of the DiarizationPort interface that processes audio in chunks.
    
    In hexagonal architecture:
    - This adapter belongs in the infrastructure layer
    - It implements a domain port (DiarizationPort)
    - It depends on infrastructure components (Pyannote Pipeline)
    - The application layer only knows about the port interface, not this implementation
    
    Note the naming convention:
    - We use a domain-focused name ("ChunkedDiarization") that describes the capability
    - We append "Adapter" to clarify its role in the architecture
    - Technical details (Pyannote) are contained in the implementation, not the class name
    """
    def __init__(
        self, 
        pipeline: Pipeline, 
        min_silence_ms: int = 600, 
        silence_thresh_db: int = -40,
        min_chunk_duration: float = 0.5,
        max_workers: int = 3,
        temp_dir: str = None
    ):
        """
        Initialize chunked diarization adapter.
        
        Args:
            pipeline: Pyannote pipeline for speaker diarization
            min_silence_ms: Minimum silence duration in milliseconds
            silence_thresh_db: Silence threshold in dB
            min_chunk_duration: Minimum chunk duration in seconds
            max_workers: Maximum number of parallel workers
            temp_dir: Directory for temporary files (uses system default if None)
        """
        self.pipeline = pipeline
        self.min_silence_ms = min_silence_ms
        self.silence_thresh_db = silence_thresh_db
        self.min_chunk_duration = min_chunk_duration
        self.max_workers = max_workers
        self.temp_dir = temp_dir
        
    async def diarize(self, clip: AudioClip) -> List[SpeakerSegment]:
        """
        Diarize the audio clip and return a list of speaker segments.
        """
        segments = [seg async for seg in self.diarize_stream(clip)]
        return segments

    async def _process_chunk(
        self, 
        clip: AudioClip, 
        chunk_start: float, 
        chunk_end: float,
        audio_segment: AudioSegment
    ) -> List[SpeakerSegment]:
        """Process a single audio chunk and return speaker segments."""
        results = []
        
        # Create a temporary file for the chunk
        with tempfile.NamedTemporaryFile(
            suffix=".wav", 
            delete=False,
            dir=self.temp_dir
        ) as tmp:
            try:
                # Extract and export the chunk
                chunk_audio = audio_segment[int(chunk_start*1000):int(chunk_end*1000)]
                chunk_audio.export(tmp.name, format="wav")
                
                # Run the pipeline
                loop = asyncio.get_running_loop()
                diarization = await loop.run_in_executor(
                    None, 
                    lambda: self.pipeline({"audio": tmp.name})
                )

                # Create speaker segments with adjusted timestamps
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    segment = SpeakerSegment(
                        audio_clip_id=clip.id,
                        start=chunk_start + turn.start,
                        end=chunk_start + turn.end,
                        speaker_label=speaker
                    )
                    results.append(segment)
                
                return results
            finally:
                # Clean up temporary file
                if os.path.exists(tmp.name):
                    os.remove(tmp.name)

    async def diarize_stream(self, clip: AudioClip) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream speaker segments as soon as they are available.
        Processes audio in chunks based on silence detection for better performance.
        Chunks are processed in parallel for faster results.
        """
        if not self.pipeline:
            raise ValueError("Diarization pipeline is not available")

        try:
            # Load the audio file once
            audio = AudioSegment.from_file(clip.file_path)
            
            # Detect chunks based on silence
            chunks = detect_chunks(
                clip.file_path, 
                min_silence_ms=self.min_silence_ms, 
                silence_thresh_db=self.silence_thresh_db,
                min_chunk_duration=self.min_chunk_duration
            )
            
            # Process chunks in batches to limit concurrent processing
            for i in range(0, len(chunks), self.max_workers):
                batch = chunks[i:i+self.max_workers]
                tasks = [
                    self._process_chunk(clip, start, end, audio)
                    for start, end in batch
                ]
                
                # Wait for all tasks in the batch to complete
                chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results in order
                for result in chunk_results:
                    if isinstance(result, Exception):
                        # Log the error but continue processing
                        print(f"Error processing chunk: {result}")
                        continue
                    
                    # Yield segments in order
                    for segment in sorted(result, key=lambda s: s.start):
                        yield segment
                        
        except Exception as e:
            # Handle any unexpected errors
            print(f"Error in diarize_stream: {e}")
            raise 