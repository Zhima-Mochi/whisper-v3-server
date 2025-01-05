from enum import Enum, auto

class OutputFormat(Enum):
    TXT = "txt"
    JSON = "json"
    SRT = "srt"

    @classmethod
    def get_default(cls):
        return cls.TXT 