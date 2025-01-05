import logging
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from typing import Optional
from constant.asr_config import ASRValidator, ASRTask


def get_asr_pipeline(
    model_name: str,
    device: str = "cuda",
    batch_size: int = 1,
    task: str = "transcribe",
    language: str = "auto",
    timestamps: bool = False,
    chunk_length_s: int = 30
):
    """
    Create and return an ASR pipeline based on input configurations.

    :param model_name: The Hugging Face model repo ID (e.g., "openai/whisper-large-v3").
    :param device: 'cuda' or 'cpu'. If 'cuda' is selected but not available, it falls back to CPU.
    :param batch_size: Number of samples to process at once.
    :param task: 'transcribe' or 'translate'. 
    :param language: Language code for transcription or target language for translation. Use 'auto' to let the model detect.
    :param timestamps: Whether to include timestamps in the output.
    :param chunk_length_s: Chunk length in seconds for long-form audio.
    :return: A HuggingFace pipeline object configured for ASR.
    """
    # Validate device
    if device == "cuda" and not torch.cuda.is_available():
        logging.warning(
            "CUDA is not available on this system. Falling back to CPU.")
        device = "cpu"
    device_str = "cuda:0" if device == "cuda" else "cpu"

    # Set appropriate torch dtype for GPU vs. CPU
    torch_dtype = torch.float16 if device_str.startswith(
        "cuda") else torch.float32

    logging.info(f"Loading model: {model_name}")
    try:
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        model.to(device_str)
        logging.info(f"Model loaded successfully on {device_str}.")
    except Exception as e:
        logging.error(f"Error loading model '{model_name}': {e}")
        raise e

    logging.info("Loading processor...")
    try:
        processor = AutoProcessor.from_pretrained(model_name)
        logging.info("Processor loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading processor for model '{model_name}': {e}")
        raise e

    # Validate task and language
    task = ASRValidator.validate_task(task)
    language = ASRValidator.validate_language(task, language)

    # Define generation kwargs based on task and language
    generation_kwargs = {}

    if task == ASRTask.TRANSLATE:
        generation_kwargs["forced_decoder_ids"] = processor.get_decoder_prompt_ids(
            language=language,
            task=task
        )
        logging.info(f"Set translation target language to '{language}'.")
    elif task == ASRTask.TRANSCRIBE and language != "auto":
        generation_kwargs["language"] = language
        logging.info(f"Set transcription source language to '{language}'.")

    logging.info("Creating pipeline...")
    # Initialize ASR pipeline
    try:
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            chunk_length_s=chunk_length_s,
            batch_size=batch_size,
            torch_dtype=torch_dtype,
            device=device_str,
            timestamps=timestamps,
            generation_kwargs=generation_kwargs,
        )
        logging.info("ASR pipeline initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize ASR pipeline: {e}")
        raise e

    logging.info("Pipeline created.")
    return asr_pipeline
