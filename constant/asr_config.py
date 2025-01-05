from enum import Enum
from typing import Optional

class ASRTask(str, Enum):
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"

class ASRValidator:
    @staticmethod
    def validate_task(task: str) -> str:
        """Validate and return the ASR task."""
        try:
            return ASRTask(task.lower())
        except ValueError:
            raise ValueError(f"Unsupported task '{task}'. Choose 'transcribe' or 'translate'.")

    @staticmethod
    def validate_language(task: str, language: str) -> str:
        """Validate and return the language based on task."""
        language = language.lower()
        
        if task == ASRTask.TRANSLATE and language == "auto":
            return "english"  # Default for translation
        
        return language 