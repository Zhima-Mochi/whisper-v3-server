import logging


class ASRTask:
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"

    def __init__(self, task: str, language: str):
        self.task = task
        self.language = language
        self.validate_task()

    def validate_task(self) -> None:
        """Validate and return the ASR task."""
        if self.task not in [self.TRANSCRIBE, self.TRANSLATE]:
            raise ValueError(
                f"Unsupported task '{self.task}'. Choose 'transcribe' or 'translate'.")
        if self.task == self.TRANSLATE and self.language == "auto":
            self.language = "en"
        elif self.task == self.TRANSCRIBE and self.language != "auto":
            logging.warning(
                f"Set transcription source language to '{self.language}'."
            )

    @property
    def pipeline_task(self) -> str:
        """Get the corresponding pipeline task name."""
        if self.task == self.TRANSCRIBE:
            return "automatic-speech-recognition"
        elif self.task == self.TRANSLATE:
            if self.language == "auto":
                return "translation"
            else:
                return f"translation_auto_to_{self.language}"
        else:
            raise ValueError(
                f"Unsupported task '{self.task}'. Choose 'transcribe' or 'translate'.")
