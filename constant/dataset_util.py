import logging

def get_librispeech_sample():
    """
    Demonstrate the pipeline on a sample from the LibriSpeech dataset
    if no local audio is provided.
    """
    logging.info("Running on the LibriSpeech dataset sample...")
    from datasets import load_dataset
    dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
    sample_audio = dataset[0]["audio"]
    return sample_audio
