from domain.repositories import TranscriptionTextRepository
from domain.transcription_text import TranscriptionText

class TranscriptionTextRepositoryImpl(TranscriptionTextRepository):
    def __init__(self):
        self._transcriptions = {}  # Dict of clip_id -> list[TranscriptionText]

    def save(self, clip_id: str, texts: list[TranscriptionText]):
        if clip_id not in self._transcriptions:
            self._transcriptions[clip_id] = []
        
        # Add new transcriptions
        self._transcriptions[clip_id].extend(texts)
        
        # Sort by start time for consistency
        self._transcriptions[clip_id].sort(key=lambda t: t.time_range.start)

    def list(self, clip_id):
        return self._transcriptions.get(clip_id, [])

    def delete(self, clip_id):
        if clip_id in self._transcriptions:
            del self._transcriptions[clip_id] 