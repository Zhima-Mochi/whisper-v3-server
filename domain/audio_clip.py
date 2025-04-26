from uuid import uuid4

class AudioClip:
    def __init__(self, file_path: str, duration: float = None):
        self.id = uuid4()
        self.file_path = file_path
        self.duration = duration  # in seconds 