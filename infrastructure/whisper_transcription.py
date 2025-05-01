import os
from faster_whisper import WhisperModel as FWWhisperModel
import torch


class WhisperModel:
    def __init__(self, model_name: str):
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "int8_float16"
            print(f"WhisperModel: Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = "cpu"
            compute_type = "float32"
            print("WhisperModel: CUDA not available, using CPU")

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
