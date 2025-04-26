from domain.services import DiarizationService, TranscriptionService
from domain.speaker_segment import SpeakerSegment
from domain.repositories import AudioClipRepository, TranscriptionTextRepository
from adapters.input.result_presenter import APIResultPresenter

class TranscribeAudioUseCase:
    def __init__(self, diarization_service: DiarizationService, transcription_service: TranscriptionService, 
                 audio_repository: AudioClipRepository, 
                 transcription_repository: TranscriptionTextRepository):
        self.diarization_service = diarization_service
        self.transcription_service = transcription_service
        self.audio_repository = audio_repository
        self.transcription_repository = transcription_repository
        self.result_presenter = APIResultPresenter()

    def execute(self, clip_id: str):
        """
        Transcribe audio file with diarization if available, otherwise do simple transcription
        """
        clip = self.audio_repository.get(clip_id)
        if not clip:
            raise ValueError(f"Audio clip {clip_id} not found")
        
        try:
            # Try to use diarization service if available
            segments = self.diarization_service.diarize(clip)
            
            # Get transcription for each segment
            for seg in segments:
                text = self.transcription_service.transcribe(
                    clip, seg.time_range.start, seg.time_range.end
                )
                # We'll attach the text directly to the segment since we don't have a separate TranscriptionText list
                seg.text = text
                
            # Use the presenter to format the result
            result = self.result_presenter.present_segments(segments)
            return result["segments"]
            
        except Exception as e:
            # If diarization fails, fall back to simple transcription
            print(f"Diarization failed: {str(e)}. Falling back to simple transcription.")
            # Create a single segment for the entire audio
            text = self.transcription_service.transcribe(clip, 0, 0)
            
            # Create a dummy segment
            segment = SpeakerSegment(
                audio_clip_id=clip.id,
                start=0.0,
                end=0.0,  # We don't know the duration
                speaker_label="UNKNOWN"
            )
            segment.text = text
            
            # Use the presenter for consistent formatting
            result = self.result_presenter.present_segments([segment])
            return result["segments"]
            
    def get_or_transcribe(self, clip_id: str):
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
        segments = self.execute(audio.file_path)
        
        # Save the transcription
        self.transcription_repository.save(clip_id, segments)
        
        # Return the transcription
        return segments
        
    def delete_transcription(self, clip_id: str):
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