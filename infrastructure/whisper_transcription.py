import os
from faster_whisper import WhisperModel as FWWhisperModel
import torch
from threading import Lock


class WhisperModel:
    _instance = None
    _lock = Lock()

    def __new__(cls, model_name: str):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str):
        if self._initialized:
            return
        self._initialized = True

        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "int8_float16"
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            compute_type = "float32"
            print("CUDA not available, using CPU")

        self.model = FWWhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            cpu_threads=os.cpu_count(),
            num_workers=1
        )

    def transcribe(self, audio_path: str, word_timestamps: bool = False) -> dict:
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language=None,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=word_timestamps
        )
        text = " ".join(seg.text for seg in segments)
        res = {
            "text": text,
        }
        return res
