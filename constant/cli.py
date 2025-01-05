"""
This file handles the command-line interface (CLI) argument parsing.
"""

import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe/Translate audio using the Whisper model."
    )
    parser.add_argument(
        "-a", "--audio", nargs="+",
        help="Path(s) to audio file(s) or directories containing audio files."
    )
    parser.add_argument(
        "-l", "--language", type=str, default="auto",
        help="Specify language (default: auto-detect)."
    )
    parser.add_argument(
        "-m", "--model", type=str, default="large-v3",
        help="Model size (tiny, base, small, medium, large-v3)."
    )
    parser.add_argument(
        "-o", "--output", type=str, default="txt",
        help="Output format (txt, srt, json)."
    )
    parser.add_argument(
        "-d", "--device", type=str, default="cuda",
        help="Device to use (cuda, cpu)."
    )
    parser.add_argument(
        "-b", "--batch_size", type=int, default=os.cpu_count(),
        help="Batch size for processing (default: number of CPU cores)."
    )
    parser.add_argument(
        "-t", "--timestamps", action="store_true",
        help="Include timestamps in the output if supported."
    )
    parser.add_argument(
        "--task", type=str, default="transcribe",
        help="Task to perform (transcribe, translate)."
    )
    parser.add_argument(
        "--silent", action="store_true",
        help="Do not print transcription to console."
    )
    parser.add_argument(
        "--output_dir", type=str, default=None,
        help="Directory to save the final output file(s)."
    )
    return parser.parse_args()
