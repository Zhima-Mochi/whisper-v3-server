import os
import shutil
import uuid
from typing import Optional
from domain.audio_clip import AudioClip
from domain.repositories import AudioClipRepository

class FileSystemAudioClipRepository(AudioClipRepository):
    def __init__(self, base_dir: str = "/tmp/voice_server_storage"):
        """Initialize storage with a permanent directory for audio files."""
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        # Keep an in-memory mapping for demo purposes
        # In a real app, this would be a database
        self.clips = {}
        
    def save(self, clip: AudioClip) -> AudioClip:
        """
        Save the audio clip to permanent storage.
        Creates a copy of the file in the storage directory.
        Returns the updated clip with the new file path.
        """
        # Generate a unique filename
        filename = f"{str(clip.id)}{os.path.splitext(clip.file_path)[1]}"
        destination = os.path.join(self.base_dir, filename)
        
        # Copy the file to storage
        try:
            shutil.copy2(clip.file_path, destination)
            
            # Update the clip's file path to point to stored location
            clip.file_path = destination
            
            # Store in our in-memory repository
            self.clips[str(clip.id)] = clip
            
            return clip
        except Exception as e:
            print(f"Error saving audio file: {str(e)}")
            # If copying fails, keep original path
            return clip
        
    def get(self, clip_id) -> Optional[AudioClip]:
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