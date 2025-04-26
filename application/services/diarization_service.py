from domain.services import DiarizationService
from domain.audio_clip import AudioClip
from domain.speaker_segment import SpeakerSegment
from domain.value_objects import TimeRange
from pyannote.audio import Pipeline

class PyannoteDiarizationService(DiarizationService):
    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    def diarize(self, clip: AudioClip) -> list[SpeakerSegment]:
        """
        Perform speaker diarization on an audio clip
        
        Raises an exception if the pipeline is not available (None)
        """
        if self.pipeline is None:
            raise ValueError("Diarization pipeline is not available. See logs for details.")
            
        diarization = self.pipeline({"audio": clip.file_path})
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(SpeakerSegment(
                audio_clip_id=clip.id,
                start=turn.start,
                end=turn.end,
                speaker_label=speaker
            ))
        return segments 