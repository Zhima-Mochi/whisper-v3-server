from domain.repositories import SpeakerSegmentRepository
from domain.speaker_segment import SpeakerSegment

class SpeakerSegmentRepositoryImpl(SpeakerSegmentRepository):
    def __init__(self):
        self._segments = {}  # Dict of clip_id -> list[SpeakerSegment]

    def save(self, clip_id: str, segments: list[SpeakerSegment]):
        if clip_id not in self._segments:
            self._segments[clip_id] = []
        
        # Add new segments
        self._segments[clip_id].extend(segments)
        
        # Sort by start time for consistency
        self._segments[clip_id].sort(key=lambda s: s.start)

    def list(self, clip_id):
        return self._segments.get(clip_id, [])

    def delete(self, clip_id):
        if clip_id in self._segments:
            del self._segments[clip_id] 