import os
import logging
from typing import Optional, Any, List


def process_audio_input(args, pipeline) -> Optional[Any]:
    """Process audio input files or use LibriSpeech sample if no input provided."""
    all_files = gather_audio_files(args.audio)
    if not all_files:
        logging.error("No valid audio files found. Exiting.")
        return None

    logging.info(f"Processing {len(all_files)} file(s)...")
    return pipeline(all_files, batch_size=args.batch_size, return_timestamps=args.return_timestamps)


def gather_audio_files(paths: List[str]) -> List[str]:
    """Gather all audio files from given paths."""
    all_files = []
    for path in paths:
        if os.path.isdir(path):
            audio_files = [
                os.path.join(path, fn)
                for fn in os.listdir(path)
                if fn.lower().endswith((".mp3", ".wav", ".flac", ".ogg", ".m4a"))
            ]
            all_files.extend(audio_files)
        else:
            all_files.append(path)
    return all_files


def write_output(output_text: str, output_dir: Optional[str], output_format: str, output_file: Optional[str]) -> None:
    """Write output to file or print to console."""
    if output_format == "stdout":
        print(output_text)
        return 0
    else:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if output_file:
            out_path = os.path.join(output_dir, output_file)
        else:
            out_path = os.path.join(output_dir, f"output.{output_format}")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        logging.info(f"Saved output to {out_path}")
        return 0
