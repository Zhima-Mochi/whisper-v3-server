import pytest
import os
from v3.main import main
from unittest.mock import patch, MagicMock, mock_open
from constant.output_format import OutputFormat

# download librispeech sample
def __init__():
    if not os.path.exists("test.wav"):
        from constant.dataset_util import get_librispeech_sample
        sample_audio = get_librispeech_sample()
        sample_audio.save("test.wav")

def test_main_with_invalid_args():
    # Test with invalid arguments
    test_args = MagicMock()
    test_args.audio = None  # Invalid audio input
    test_args.model = "invalid_model"
    test_args.output = "invalid_format"
    
    with patch('argparse.ArgumentParser.parse_args', return_value=test_args):
        with pytest.raises(Exception):
            main()

@pytest.mark.parametrize("output_format", ["txt", "srt", "json"])
def test_main_with_different_outputs(output_format):
    test_args = MagicMock()
    test_args.audio = ["test.wav"]
    test_args.language = "auto"
    test_args.model = "tiny"
    test_args.output = output_format
    test_args.device = "cpu"
    test_args.batch_size = 1
    test_args.timestamps = True
    test_args.task = "transcribe"
    test_args.silent = True
    test_args.output_dir = "test_output"

    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [{"text": "Test", "chunks": [{"text": "Test", "timestamp": (0.0, 1.0)}]}]

    with patch('argparse.ArgumentParser.parse_args', return_value=test_args), \
         patch('v3.pipeline_util.get_asr_pipeline', return_value=mock_pipeline), \
         patch('os.makedirs'), \
         patch('builtins.open', mock_open()):
        
        result = main()
        assert result == 0

def test_main_with_librispeech_fallback():
    test_args = MagicMock()
    test_args.audio = None
    test_args.language = "auto"
    test_args.model = "tiny"
    test_args.output = "txt"
    test_args.device = "cpu"
    test_args.batch_size = 1
    test_args.timestamps = False
    test_args.task = "transcribe"
    test_args.silent = True
    test_args.output_dir = None

    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [{"text": "LibriSpeech test"}]
    mock_audio = {"array": [0.1, 0.2, 0.3], "sampling_rate": 16000}

    with patch('argparse.ArgumentParser.parse_args', return_value=test_args), \
         patch('v3.pipeline_util.get_asr_pipeline', return_value=mock_pipeline), \
         patch('constant.dataset_util.get_librispeech_sample', return_value=mock_audio):
        
        result = main()
        assert result == 0

def test_main_with_translation():
    test_args = MagicMock()
    test_args.audio = ["test.wav"]
    test_args.language = "fr"  # French
    test_args.model = "tiny"
    test_args.output = "txt"
    test_args.device = "cpu"
    test_args.batch_size = 1
    test_args.timestamps = False
    test_args.task = "translate"
    test_args.silent = True
    test_args.output_dir = None

    mock_pipeline = MagicMock()
    mock_pipeline.return_value = [{"text": "Translated text"}]

    with patch('argparse.ArgumentParser.parse_args', return_value=test_args), \
         patch('v3.pipeline_util.get_asr_pipeline', return_value=mock_pipeline):
        
        result = main()
        assert result == 0
        # Verify pipeline was called with correct parameters
        mock_pipeline.assert_called_once()
