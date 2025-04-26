from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch

class WhisperModel:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.processor = AutoProcessor.from_pretrained(model_name)
        
        # Check if CUDA is available and set device accordingly
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Set appropriate torch dtype for GPU vs. CPU
        torch_dtype = torch.float16 if device_str.startswith("cuda") else torch.float32
        
        # Load the model with appropriate settings
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True
        )
        
        # Move model to the appropriate device
        self.model = self.model.to(device_str)
        
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            generate_kwargs={"max_new_tokens": 128},
            chunk_length_s=30,
            batch_size=1,  # Lower batch size for memory conservation
            return_timestamps=True,
            device=device_str
        )

    def transcribe(self, audio_path: str, word_timestamps: bool = False) -> dict:
        result = self.pipe(audio_path, return_timestamps=word_timestamps)
        return result 