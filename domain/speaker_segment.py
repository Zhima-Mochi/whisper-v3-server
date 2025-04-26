from uuid import uuid4
from .value_objects import TimeRange

class SpeakerSegment:
    def __init__(self, audio_clip_id, start: float, end: float, speaker_label: str, text: str = None):
        self.id = uuid4()
        self.audio_clip_id = audio_clip_id
        self.time_range = TimeRange(start, end)
        self.speaker_label = speaker_label
        self.text = text