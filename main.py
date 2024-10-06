#!/usr/bin/env python3

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import argparse
import logging
import os
import warnings

# Suppress the specific warning about PipelineChunkIterator length
warnings.filterwarnings("ignore", category=UserWarning, message="Length of IterableDataset")

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
            chunk_length_s=30,  # Enable chunked long-form transcription
            batch_size=os.cpu_count(), # Use all available CPU cores
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
        help="Path to the audio file or directory to transcribe",
    )

    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        help="Directory to save the transcribed text",
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
        output_dir = args.output_path if args.output_path else args.audio_path
        # Check if the provided path is a directory or a file
        if os.path.isdir(args.audio_path):
            # If it's a directory, transcribe all audio files in the directory
            audio_files = [
                os.path.join(args.audio_path, filename)
                for filename in os.listdir(args.audio_path)
                if filename.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".m4a"))
            ]
            transcribe_audio(audio_files, output_dir, args.silent)
        else:
            # If it's a single file, transcribe it
            transcribe_audio([args.audio_path], output_dir, args.silent)
    else:
        run_on_dataset()


def transcribe_audio(file_paths, output_dir=None, silent=False):
    if len(file_paths) == 0:
        logging.error("No audio files found")
        return
    pipe = get_pipe()
    results = pipe(file_paths, batch_size=len(file_paths))

    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    for file_path, result in zip(file_paths, results):
        if output_dir:
            output_file = os.path.join(output_dir, f"{os.path.basename(file_path)}.txt")
            with open(output_file, "w") as f:
                f.write(result["text"])
            logging.info(f"Transcribed text saved to {output_file}")
        else:
            if not silent:
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