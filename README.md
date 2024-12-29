# whisper

## Performance Tips

1. **GPU Acceleration**
   - The tool automatically detects and uses your GPU if available
   - Expect 5-10x faster processing with a CUDA-compatible GPU

2. **Memory Usage**
   - The model requires ~6GB of storage when first downloaded
   - For optimal performance, ensure at least 16GB of RAM

3. **Long Audio Files**
   - Files are automatically processed in 30-second chunks
   - This allows for efficient processing of long recordings

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**
   ```bash
   # Check if CUDA is detected
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Memory Errors**
   - Try reducing `batch_size` if you encounter memory issues
   - Default batch size uses all CPU cores

3. **Audio Format Issues**
   - Ensure your audio files are in supported formats
   - Convert unsupported formats using tools like `ffmpeg`

## Advanced Configuration

The tool uses these default settings:
- Chunk length: 30 seconds
- Batch size: Number of CPU cores
- Model: whisper-large-v3
- Device: CUDA if available, CPU otherwise

## Acknowledgments

- Based on OpenAI's Whisper Large V3 model
- Uses Hugging Face's Transformers library
