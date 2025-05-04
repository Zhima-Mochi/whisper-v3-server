from domain.repositories import AudioClipRepository
from domain.audio_clip import AudioClip

class AudioClipRepositoryImpl(AudioClipRepository):
    def __init__(self):
        self._clips = {}  # In-memory storage for simplicity

    def save(self, clip: AudioClip):
        self._clips[str(clip.id)] = clip

    def get(self, clip_id):
        return self._clips.get(clip_id)

    def delete(self, clip_id):
        if clip_id in self._clips:
            del self._clips[clip_id] 