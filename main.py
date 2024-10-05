#!/usr/bin/env python3

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor
import soundfile as sf

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
        help="Path to the audio file or directory to transcribe",
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
        # Check if the provided path is a directory or a file
        if os.path.isdir(args.audio_path):
            # If it's a directory, transcribe all audio files in the directory
            with ThreadPoolExecutor() as executor:
                futures = []
                for filename in os.listdir(args.audio_path):
                    # Ensure it's an audio file (e.g., by checking the extension)
                    if filename.endswith((".mp3", ".wav", ".flac", ".ogg")):
                        file_path = os.path.join(args.audio_path, filename)
                        output_file = None

                        # If output_path is a directory, save each transcription to a separate file
                        if args.output_path and os.path.isdir(args.output_path):
                            output_file = os.path.join(args.output_path, f"{filename}.txt")

                        futures.append(executor.submit(transcribe_audio, file_path, output_file, args.silent))
                for future in futures:
                    future.result()
        else:
            # If it's a single file, transcribe it
            transcribe_audio(args.audio_path, args.output_path, args.silent)
    else:
        run_on_dataset()


def transcribe_audio(file_path, output_path=None, silent=False):
    pipe = get_pipe()
    with sf.SoundFile(file_path) as f:
        for block in f.blocks(blocksize=1024):
            result = pipe()(block, return_timestamps=True)
            if output_path:
                with open(output_path, "a") as f:
                    f.write(result["text"])
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