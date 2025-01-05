"""
This file handles the command-line interface (CLI) argument parsing.
"""

import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcribe audio using the Whisper model."
    )
    parser.add_argument(
        "-a", "--audio", nargs="+",
        help="Path(s) to audio file(s) or directories containing audio files."
    )
    parser.add_argument(
        "-m", "--model", type=str, default="large-v3",
        help="Model size (tiny, base, small, medium, large-v3)."
    )
    parser.add_argument(
        "-f", "--output_format", type=str, default="text",
        help="Output format (text, srt, json)."
    )
    parser.add_argument(
        "--print_output", action="store_true",
        help="Print the output to the console."
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
        "--return_timestamps", action="store_true",
        help="Include timestamps in the output if supported."
    )
    parser.add_argument(
        "-t", "--task", type=str, default="transcribe",
        help="Task to perform (transcribe only)."
    )
    parser.add_argument(
        "-s", "--silent", action="store_true",
        help="Do not print transcription to console."
    )
    parser.add_argument(
        "-o", "--output_dir", type=str, default=None,
        help="Directory to save the final output file(s)."
    )
    parser.add_argument(
        "-of", "--output_file", type=str, default=None,
        help="File to save the final output to."
    )
    return parser.parse_args()
