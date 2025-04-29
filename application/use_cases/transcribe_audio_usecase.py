from typing import AsyncGenerator
from domain.services import DiarizationService, TranscriptionService
from domain.speaker_segment import SpeakerSegment
from domain.repositories import AudioClipRepository, TranscriptionTextRepository


class TranscribeAudioUseCase:
    def __init__(self, diarization_service: DiarizationService, transcription_service: TranscriptionService,
                 audio_repository: AudioClipRepository,
                 transcription_repository: TranscriptionTextRepository):
        self.diarization_service = diarization_service
        self.transcription_service = transcription_service
        self.audio_repository = audio_repository
        self.transcription_repository = transcription_repository

    async def execute(self, clip_id: str) -> list[SpeakerSegment]:
        """
        Transcribe audio file with diarization if available, otherwise do simple transcription
        """
        clip = self.audio_repository.get(clip_id)
        if not clip:
            raise ValueError(f"Audio clip {clip_id} not found")

        try:
            # Try to use diarization service if available
            segments = await self.diarization_service.diarize(clip)

            # Get transcription for each segment
            for seg in segments:
                text = await self.transcription_service.transcribe(
                    clip, seg.time_range.start, seg.time_range.end
                )
                # We'll attach the text directly to the segment since we don't have a separate TranscriptionText list
                seg.text = text

            self.transcription_repository.save(clip_id, segments)

            return segments

        except Exception as e:
            # If diarization fails, fall back to simple transcription
            print(
                f"Diarization failed: {str(e)}. Falling back to simple transcription.")
            # Create a single segment for the entire audio
            text = await self.transcription_service.transcribe(clip, 0, 0)

            # Create a dummy segment
            segment = SpeakerSegment(
                audio_clip_id=clip.id,
                start=0.0,
                end=0.0,  # We don't know the duration
                speaker_label="UNKNOWN"
            )
            segment.text = text

            return [segment]

    async def get_or_transcribe(self, clip_id: str):
        """
        Get a transcription from the repository if it exists,
        otherwise transcribe the audio and save the result

        Args:
            clip_id: ID of the audio clip

        Returns:
            List of transcription segments
        """
        # First try to get existing transcription
        transcription = self.transcription_repository.list(clip_id)
        if transcription:
            return transcription

        # If no transcription exists, get the audio clip
        audio = self.audio_repository.get(clip_id)
        if not audio:
            raise ValueError(f"Audio clip {clip_id} not found")

        # Transcribe the audio
        segments = await self.execute(audio.file_path)

        # Save the transcription
        self.transcription_repository.save(clip_id, segments)

        # Return the transcription
        return segments

    async def delete_transcription(self, clip_id: str):
        """
        Delete a transcription from the repository

        Args:
            clip_id: ID of the audio clip

        Returns:
            bool: True if successful, False if not found

        Raises:
            Exception: If deletion fails
        """
        success = self.transcription_repository.delete(clip_id)
        if not success:
            raise Exception(f"Deletion failed for clip {clip_id}")
        return True

    async def execute_streaming(self, clip_id: str) -> AsyncGenerator[SpeakerSegment, None]:
        """
        Stream transcription segments for a clip:
        1) attempt async diarization
        2) for each segment, do async transcription and yield formatted text
        3) fallback to simple transcription if diarization fails
        """
        clip = self.audio_repository.get(clip_id)
        if not clip:
            raise ValueError(f"Audio clip {clip_id} not found")

        try:
            # Stream diarization segments
            async for seg in self.diarization_service.diarize_stream(clip):
                # Collect all text chunks into a single string
                text_chunks = []
                async for chunk in self.transcription_service.transcribe_stream(
                    clip, seg.time_range.start, seg.time_range.end
                ):
                    text_chunks.append(chunk)

                seg.text = " ".join(text_chunks)
                yield seg

        except Exception as e:
            # Fallback: single-segment transcription
            print(
                f"Diarization failed: {e}. Falling back to simple transcription.")
            text = await self.transcription_service.transcribe_stream(clip, 0, 0)
            seg = SpeakerSegment(
                audio_clip_id=clip.id,
                start=0.0,
                end=0.0,
                speaker_label="UNKNOWN"
            )
            seg.text = text
            yield seg

    async def get_or_transcribe_streaming(self, clip_id: str) -> AsyncGenerator[SpeakerSegment, None]:
        """
        If existing transcription exists, stream it.
        Otherwise, stream a fresh transcription.
        """
        existing = self.transcription_repository.list(clip_id)
        if existing:
            for seg in existing:
                yield seg
            return

        segments = []
        # No existing transcription: run streaming
        async for seg in self.execute_streaming(clip_id):
            segments.append(seg)
            yield seg

        if segments:
            # Save the transcription
            self.transcription_repository.save(clip_id, segments)
        return