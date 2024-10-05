#!/usr/bin/env python3

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import argparse
import logging

logging.basicConfig(level=logging.INFO)


def get_pipe():
    pipe = None

    def f(*args, **kwargs):
        nonlocal pipe
        if pipe:
            logging.info("Reusing existing pipeline")
            return pipe(*args, **kwargs)

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {device}")

        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "openai/whisper-large-v3"

        logging.info(f"Loading model: {model_id}")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        model.to(device)
        logging.info(f"Model loaded: {model_id}")

        logging.info(f"Loading processor for model: {model_id}")
        processor = AutoProcessor.from_pretrained(model_id)
        logging.info(f"Processor loaded: {model_id}")

        logging.info("Creating pipeline")
        pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device
        )
        logging.info("Pipeline created")

        return pipe(*args, **kwargs)

    return f


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio using the Whisper model"
    )

    parser.add_argument(
        "-a",
        "--audio-path",
        type=str,
        help="Path to the audio file to transcribe",
    )

    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        help="Path to save the transcribed text",
    )

    parser.add_argument(
        "--silent",
        action="store_true",
        help="Don't print the transcribed text to the console",
    )

    args = parser.parse_args()

    if args.silent:
        logging.disable(logging.INFO)

    if args.audio_path:
        with open(args.audio_path, "rb") as f:
            data = f.read()
        transcribe_audio(data, args.output_path)
    else:
        run_on_dataset()


def transcribe_audio(data, output_path=None):
    pipe = get_pipe()
    result = pipe()(data, return_timestamps=True)
    if output_path:
        with open(output_path, "w") as f:
            f.write(result["text"])
            logging.info(f"Transcribed text saved to {output_path}")
    else:
        print(result["text"])


def run_on_dataset():
    logging.info("Running on the LibriSpeech dataset")
    from datasets import load_dataset
    dataset = load_dataset(
        "distil-whisper/librispeech_long", "clean", split="validation")
    sample = dataset[0]["audio"]

    pipe = get_pipe()
    result = pipe(sample, return_timestamps=True)
    print(result["text"])


if __name__ == "__main__":
    main()
