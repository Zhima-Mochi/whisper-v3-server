#!/usr/bin/env python3

import logging
from constant.cli import default_parser
from v3.pipeline_util import get_asr_pipeline
from helper.srt_util import convert_to_srt
from constant.model_util import get_model_name
from v3.audio_processing import process_audio_input, write_output
from constant.output_format import TXT, JSON, SRT, DEFAULT_FORMAT
from helper.output_converter import get_converter
from constant.dataset_util import get_librispeech_sample
logging.basicConfig(level=logging.INFO)

def main():
    args = default_parser().parse_args()
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
        timestamps=args.timestamps
    )

    # Process audio and get results
    results = process_audio_input(args, asr_pipeline)
    if results is None:
        return

    # Convert and output results
    output_text = convert_pipeline_output(results, args.output, args.timestamps)
    write_output(output_text, args.output_dir, args.output, args.silent)


def convert_pipeline_output(pipe_result, output_format, timestamps=False):
    """
    Convert the Hugging Face pipeline output into the specified format (txt, srt, json).
    """
    if isinstance(pipe_result, dict):
        pipe_result = [pipe_result]
    
    converter = get_converter(output_format)
    return converter.convert(pipe_result, timestamps)


if __name__ == "__main__":
    main()
