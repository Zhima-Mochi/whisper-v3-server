from dataclasses import dataclass, field
from uuid import UUID, uuid4
from .value_objects import TimeRange


@dataclass
class SpeakerSegment:
    id: UUID = field(default_factory=uuid4)
    audio_clip_id: UUID = None
    start: float = None
    end: float = None
    speaker_label: str = None
    text: str = None

    @property
    def time_range(self) -> TimeRange:
        return TimeRange(self.start, self.end)

    def to_dict(self):
        return {
            "id": str(self.id),
            "audio_clip_id": str(self.audio_clip_id),
            "start": self.start,
            "end": self.end,
            "speaker_label": self.speaker_label,
            "text": self.text
        }
