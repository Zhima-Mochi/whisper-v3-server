"""
Utility functions for handling Whisper model configurations and mappings.
"""

# Map user-friendly model size names to HuggingFace repo IDs
MODEL_MAP = {
    "tiny": "openai/whisper-tiny",
    "base": "openai/whisper-base",
    "small": "openai/whisper-small",
    "medium": "openai/whisper-medium",
    "large-v3": "openai/whisper-large-v3"
}

def get_model_name(model_size: str) -> str:
    """
    Convert user-friendly model size to actual HuggingFace repository name.
    
    Args:
        model_size: User-friendly model size (tiny, base, small, medium, large-v3)
        
    Returns:
        str: HuggingFace repository name for the model
    """
    if model_size not in MODEL_MAP:
        raise ValueError(f"Invalid model size: {model_size}. Please choose from: {', '.join(MODEL_MAP.keys())}")
    return MODEL_MAP[model_size]