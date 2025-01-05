#!/usr/bin/env python3

import logging
from constant.cli import parse_args
from v3.pipeline_util import get_asr_pipeline
from constant.model_util import get_model_name
from v3.audio_processing import process_audio_input, write_output
from helper.output_converter import get_converter
from constant.dataset_util import get_librispeech_sample

logging.basicConfig(level=logging.INFO)


def main():
    args = parse_args()
    if args.silent:
        logging.disable(logging.INFO)
    if args.audio is None:
        args.audio = get_librispeech_sample(args.timestamps, args.output)

    # Get model name from user-friendly size
    model_name = get_model_name(args.model)

    # Build the pipeline
    asr_pipeline = get_asr_pipeline(
        model_name=model_name,
        device=args.device,
        batch_size=args.batch_size,
        task=args.task,
        language=args.language,
        return_timestamps=args.return_timestamps
    )

    # Process audio and get results
    results = process_audio_input(args, asr_pipeline)
    if results is None:
        return 1

    # Convert and output results
    output_text = convert_pipeline_output(
        results, args.output_format, args.return_timestamps)
    
    output_file = args.output_file
    if output_file is None:
        print(output_text)
        return 0
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = "."
    write_output(output_text, output_dir, output_file)
    if args.print_output:
        print(output_text)

    return 0


def convert_pipeline_output(pipe_result, output_format, return_timestamps=False):
    """
    Convert the Hugging Face pipeline output into the specified format (text, srt, json).
    """
    if isinstance(pipe_result, dict):
        pipe_result = [pipe_result]

    converter = get_converter(output_format)
    return converter.convert(pipe_result, return_timestamps)


if __name__ == "__main__":
    main()
