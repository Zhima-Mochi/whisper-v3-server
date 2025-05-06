import json
import os
import shutil
from typing import Optional
from domain.audio_clip import AudioClip
from domain.repositories import AudioClipRepository, TranscriptionTextRepository
from domain.speaker_segment import SpeakerSegment

class FileSystemAudioClipRepository(AudioClipRepository):
    """
    File system implementation of the AudioClipRepository.
    This is an outbound adapter in the hexagonal architecture.
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _get_file_path(self, clip_id: str) -> str:
        """Get the full file path for an audio clip"""
        return os.path.join(self.storage_path, f"{clip_id}.wav")

    def save(self, clip: AudioClip) -> AudioClip:
        """Save an audio clip to the file system"""
        file_path = self._get_file_path(str(clip.id))
        
        # Save the audio content
        with open(file_path, 'wb') as f:
            f.write(clip.content)
        
        # Update the clip with the file path
        clip.file_path = file_path
        return clip

    def get(self, clip_id: str) -> Optional[AudioClip]:
        """Get an audio clip from the file system"""
        file_path = self._get_file_path(clip_id)
        if not os.path.exists(file_path):
            return None

        # Read the audio content
        with open(file_path, 'rb') as f:
            content = f.read()

        # Create and return the audio clip
        clip = AudioClip(
            id=clip_id,
            title=os.path.basename(file_path),
            filename=os.path.basename(file_path),
            content=content,
            file_path=file_path
        )
        return clip

    def delete(self, clip_id: str) -> bool:
        """Delete an audio clip from the file system"""
        file_path = self._get_file_path(clip_id)
        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)
            return True
        except Exception:
            return False 
        
class FileSystemTranscriptionTextRepository(TranscriptionTextRepository):
    """
    File system implementation of the TranscriptionTextRepository.
    This is an outbound adapter in the hexagonal architecture.
    """
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def _get_file_path(self, clip_id: str) -> str:
        """Get the full file path for a transcription text"""
        return os.path.join(self.storage_path, f"{clip_id}.json")

    def save(self, clip_id: str, segments: list[SpeakerSegment]) -> None:
        """Save a list of speaker segments to the file system"""
        file_path = self._get_file_path(clip_id)
        with open(file_path, 'w') as f:
            json.dump([seg.to_dict() for seg in segments], f)


    def list(self, clip_id: str) -> list[SpeakerSegment]:
        """List all speaker segments for a given clip ID"""
        file_path = self._get_file_path(clip_id)
        if not os.path.exists(file_path):
            return []

        with open(file_path, 'r') as f:
            segments = json.load(f)

        return [SpeakerSegment(**seg) for seg in segments]

    def delete(self, clip_id: str) -> bool:
        """Delete a transcription text from the file system""" 
        file_path = self._get_file_path(clip_id)
        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)
            return True
        except Exception:
            return False
