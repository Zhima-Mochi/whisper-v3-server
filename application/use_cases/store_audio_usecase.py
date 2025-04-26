from domain.audio_clip import AudioClip
from domain.repositories import AudioClipRepository
from uuid import uuid4


class StoreAudioUseCase:
    """Use case for storing audio clips in the repository"""

    def __init__(self, audio_repository: AudioClipRepository):
        """
        Initialize with an audio repository

        Args:
            audio_repository: Optional AudioClipRepository instance
        """
        self.audio_repository = audio_repository

    def execute(self, file_path: str) -> AudioClip:
        """
        Store an audio file and return the audio clip object

        Args:
            file_path: Path to the audio file to store

        Returns:
            AudioClip: The stored audio clip with its ID
        """
        # Create an audio clip
        clip = AudioClip(file_path=file_path)
        clip.id = uuid4()  # Generate a new ID

        # Save it to the repository
        saved_clip = self.audio_repository.save(clip)

        return saved_clip

    def get_clip(self, clip_id) -> AudioClip:
        """
        Retrieve an audio clip by its ID

        Args:
            clip_id: The ID of the clip to retrieve

        Returns:
            AudioClip: The retrieved audio clip, or None if not found
        """
        return self.audio_repository.get(clip_id)

    def delete_clip(self, clip_id) -> bool:
        """
        Delete an audio clip by its ID

        Args:
            clip_id: The ID of the clip to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        return self.audio_repository.delete(clip_id)
