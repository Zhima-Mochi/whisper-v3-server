from pyannote.audio import Pipeline
from config import HUGGINGFACE_AUTH_TOKEN

_pyannote_pipeline = None

def load_pyannote_pipeline(model_name):
    """
    Load a pyannote Pipeline instance (singleton pattern)
    
    Args:
        model_name: Name of the pyannote model to load
        
    Returns:
        An instance of pyannote Pipeline
    """
    global _pyannote_pipeline
    if _pyannote_pipeline is None:
        _pyannote_pipeline = Pipeline.from_pretrained(
            model_name,
            use_auth_token=HUGGINGFACE_AUTH_TOKEN
        )
    return _pyannote_pipeline
