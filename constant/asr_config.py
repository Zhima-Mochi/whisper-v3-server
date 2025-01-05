import logging


class ASRTask:
    TRANSCRIBE = "transcribe"

    def __init__(self, task: str):
        self.task = task
        self.validate_task()

    def validate_task(self) -> None:
        """Validate and return the ASR task."""
        if self.task != self.TRANSCRIBE:
            raise ValueError(f"Unsupported task '{self.task}'. Only 'transcribe' is supported.")

    @property
    def pipeline_task(self) -> str:
        """Get the corresponding pipeline task name."""
        return "automatic-speech-recognition"
