# whisper

A powerful speech-to-text transcription tool based on OpenAI's Whisper Large V3 model.

## Features

- High-accuracy transcription in 100+ languages
- Automatic language detection
- Timestamp generation for each segment
- GPU acceleration support
- Batch processing capabilities
- Format conversion and subtitle generation

## Installation

```bash
# Using pip
pip install whisper-v3

# Using conda
conda install -c conda-forge whisper-v3
```

## Quick Start

Basic transcription:
```bash
whisper-v3 -a <audio_file>
```

With language specification:
```bash
whisper-v3 -a <audio_file> --language "English"
```

## Detailed Usage

### Command Line Options

```bash
whisper-v3 [options] <audio_file>

Options:
  -a, --audio        Path to audio file(s)
  -l, --language     Specify language (default: auto-detect)
  -m, --model        Model size (tiny, base, small, medium, large-v3)
  -o, --output       Output format (text, srt, json)
  -d, --device       Device to use (cuda, cpu)
  -b, --batch_size   Batch size for processing
  -t, --timestamps   Include timestamps in output
  --task            Task to perform (transcribe)
```

### Examples

1. **Basic Transcription**
   ```bash
   whisper-v3 -a audio.mp3
   ```

2. **Specify Output Format**
   ```bash
   whisper-v3 -a audio.mp3 -o srt
   ```

3. **Batch Processing**
   ```bash
   whisper-v3 -a folder/*.mp3 -b 4
   ```

## Performance Tips

1. **GPU Acceleration**
   - The tool automatically detects and uses your GPU if available
   - Expect 5-10x faster processing with a CUDA-compatible GPU
   - Supports both NVIDIA (CUDA) and AMD (ROCm) GPUs

2. **Memory Usage**
   - The model requires ~6GB of storage when first downloaded
   - For optimal performance, ensure at least 16GB of RAM
   - Large-v3 model may require up to 12GB VRAM for GPU processing

3. **Long Audio Files**
   - Files are automatically processed in 30-second chunks
   - This allows for efficient processing of long recordings
   - Progress bar shows estimated completion time

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**
   ```bash
   # Check if CUDA is detected
   python -c "import torch; print(torch.cuda.is_available())"
   
   # Check CUDA version
   nvidia-smi
   ```

2. **Memory Errors**
   - Try reducing `batch_size` if you encounter memory issues
   - Default batch size uses all CPU cores
   - Use `--device cpu` if GPU memory is insufficient

3. **Audio Format Issues**
   - Supported formats: mp3, wav, m4a, flac, ogg
   - Convert unsupported formats using ffmpeg:
     ```bash
     ffmpeg -i input.wma output.mp3
     ```

## Advanced Configuration

The tool uses these default settings:
- Chunk length: 30 seconds
- Batch size: Number of CPU cores
- Model: whisper-large-v3
- Device: CUDA if available, CPU otherwise

### Custom Configuration File

Create `config.yaml` in your working directory:
```yaml
model: large-v3
language: auto
output_format: srt
batch_size: 4
device: cuda
```

## Output Formats

1. **Text (.txt)**
   - Plain text transcription
   - Optional timestamps

2. **SubRip (.srt)**
   - Standard subtitle format
   - Includes timestamps and sequence numbers

3. **WebVTT (.vtt)**
   - Web-friendly subtitle format
   - Compatible with HTML5 video

4. **JSON**
   - Detailed output including:
     - Word-level timestamps
     - Confidence scores
     - Speaker detection (if enabled)

## Acknowledgments

- Based on OpenAI's Whisper Large V3 model
- Uses Hugging Face's Transformers library
- Community contributions and improvements