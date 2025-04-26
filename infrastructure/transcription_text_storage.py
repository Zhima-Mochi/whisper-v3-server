import json
import os
import shutil
import uuid
from typing import Optional
from domain.audio_clip import AudioClip
from domain.repositories import TranscriptionTextRepository
from domain.transcription_text import TranscriptionText


class FileSystemTranscriptionTextRepository(TranscriptionTextRepository):
    def __init__(self, base_dir: str = "/tmp/whisper_v3_server_storage/transcription_texts"):
        """Initialize storage with a permanent directory for audio files."""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        # Keep an in-memory mapping for demo purposes
        # In a real app, this would be a database
        self.clips = {}
        
    def save(self, clip_id: str, texts: list[TranscriptionText]) -> list[TranscriptionText]:
        """
        Save the transcription text to permanent storage.
        Creates a copy of the file in the storage directory.
        Returns the updated clip with the new file path.
        """
        # Generate a unique filename
        filename = f"{clip_id}.json"
        destination = os.path.join(self.base_dir, filename)
        
        # Copy the file to storage
        try:
            with open(destination, 'w') as f:
                json.dump(texts, f)
            
            # Store in our in-memory repository
            self.clips[str(clip_id)] = texts
            
            return texts
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")
            # If copying fails, keep original path
            return texts
        
    def list(self, clip_id) -> Optional[list[TranscriptionText]]:
        """
        Retrieve a clip by ID.
        Returns None if clip is not found.
        """
        clip_id_str = str(clip_id)
        
        # First check in-memory storage
        if clip_id_str in self.clips:
            return self.clips[clip_id_str]
            
        # Check if file exists in storage directory
        for filename in os.listdir(self.base_dir):
            file_id = os.path.splitext(filename)[0]
            if file_id == clip_id_str:
                file_path = os.path.join(self.base_dir, filename)
                # Create new clip and add to in-memory storage
                clip = AudioClip(file_path=file_path)
                clip.id = uuid.UUID(clip_id_str)
                self.clips[clip_id_str] = clip
                return clip
                
        return None
        
    def delete(self, clip_id) -> bool:
        """
        Delete a clip from storage.
        Returns True if successful, False otherwise.
        """
        clip = self.get(clip_id)
        if not clip:
            return True
            
        try:
            # Remove file
            if os.path.exists(clip.file_path):
                os.remove(clip.file_path)
                
            # Remove from in-memory storage
            if str(clip_id) in self.clips:
                del self.clips[str(clip_id)]
                
            return True
        except Exception as e:
            print(f"Error deleting audio file: {str(e)}")
            return False 