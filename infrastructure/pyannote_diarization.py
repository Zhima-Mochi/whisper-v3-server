from pyannote.audio import Pipeline
import warnings
from config import HUGGINGFACE_TOKEN
import torch


def load_pyannote_pipeline(model_name: str) -> Pipeline:
    """
    Load the pyannote pipeline using the Hugging Face token from config.

    Note: For 'pyannote/speaker-diarization', this requires authentication
    and acceptance of the model's usage terms. Visit:
    https://huggingface.co/pyannote/speaker-diarization to accept the terms
    and get an access token.

    """
    # if torch.cuda.is_available():
    #     device = "cuda"
    #     print(
    #         f"PyannotePipeline: Using GPU: {torch.cuda.get_device_name(0)}")
    # else:
    #     device = "cpu"
    #     print("PyannotePipeline: CUDA not available, using CPU")
    device = "cpu"
    # Attempt to load the model with authentication token
    if not HUGGINGFACE_TOKEN:
        warnings.warn(
            f"HUGGINGFACE_TOKEN not set in environment or .env file.\n"
            f"Please set this variable to access gated models like '{model_name}'.\n"
            f"Visit https://huggingface.co/settings/tokens to get your token."
        )
        pipeline = Pipeline.from_pretrained(model_name)
    else:

        pipeline = Pipeline.from_pretrained(
            model_name, use_auth_token=HUGGINGFACE_TOKEN)

    pipeline.to(torch.device(device))
    return pipeline
