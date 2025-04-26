from uuid import uuid4
from .value_objects import TimeRange

class TranscriptionText:
    def __init__(self, audio_clip_id, text: str, start: float, end: float, speaker_label: str = None):
        self.id = uuid4()
        self.audio_clip_id = audio_clip_id
        self.text = text
        self.time_range = TimeRange(start, end)
        self.speaker_label = speaker_label 