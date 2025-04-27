from typing import AsyncGenerator
from domain.services import TranscriptionService
from domain.audio_clip import AudioClip
import os
from shared.utils.audio_converter import convert_to_wav
from pydub import AudioSegment
from infrastructure.whisper_transcription import WhisperModel


class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, model: WhisperModel):
        self.model = model

    async def transcribe(self, clip: AudioClip, start: float, end: float) -> str:
        """
        Transcribe audio segment from start to end time.
        If start and end times are specified, extracts the segment before transcription.
        """
        segments = []
        async for segment in self.transcribe_stream(clip, start, end):
            segments.append(segment)
        return " ".join(segments)

    async def transcribe_stream(self, clip: AudioClip, start: float, end: float) -> AsyncGenerator[str, None]:
        """
        Stream transcription segments for an audio clip.

        Args:
            clip: The audio clip to transcribe
            start: The start time of the segment to transcribe
            end: The end time of the segment to transcribe

        Returns:
            An async generator of transcription segments
        """
        try:
            # Convert to WAV format first if needed
            wav_path = clip.file_path
            if not clip.file_path.lower().endswith('.wav'):
                wav_path = f"{os.path.splitext(clip.file_path)[0]}.wav"
                convert_to_wav(clip.file_path, wav_path)

            # If we need to extract a segment
            if start > 0 or (end > 0 and end < clip.duration):
                # Extract segment using pydub
                audio = AudioSegment.from_wav(wav_path)
                # Convert seconds to milliseconds
                start_ms = int(start * 1000)
                end_ms = int(end * 1000) if end > 0 else len(audio)
                segment = audio[start_ms:end_ms]

                # Save the segment to a temporary file
                temp_segment_path = f"/tmp/segment_{os.path.basename(wav_path)}"
                segment.export(temp_segment_path, format="wav")

                # Transcribe the segment
                result = self.model.transcribe(
                    temp_segment_path, word_timestamps=True)

                # Clean up
                if os.path.exists(temp_segment_path):
                    os.remove(temp_segment_path)

                # Handle the transformers pipeline output format
                if isinstance(result, dict) and "text" in result:
                    yield result["text"].strip()
                else:
                    # For transformers pipeline output
                    yield result.strip()

            else:
                # Process full audio
                result = self.model.transcribe(wav_path, word_timestamps=True)

                # Handle the transformers pipeline output format
                if isinstance(result, dict) and "text" in result:
                    yield result["text"].strip()
                else:
                    # For transformers pipeline output
                    yield result.strip()

        except Exception as e:
            # Log error and return empty generator
            print(f"Error transcribing audio: {str(e)}")
