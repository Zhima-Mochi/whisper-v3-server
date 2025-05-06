from uuid import uuid4

class AudioClip:
    def __init__(self, title: str, filename: str, content: bytes, duration: float = None):
        self.id = uuid4()
        self.title = title
        self.filename = filename
        self.content = content
        self.duration = duration  # in seconds 

    def get_file_path(self):
        return f"{self.id}.wav"