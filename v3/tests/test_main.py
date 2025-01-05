import pytest
import os
import soundfile as sf
from v3.main import main
from unittest.mock import patch, MagicMock

# download librispeech sample
@pytest.fixture(scope="session", autouse=True)
def setup_test_audio():
    if not os.path.exists("test.wav"):
        from constant.dataset_util import get_librispeech_sample
        sample_audio = get_librispeech_sample()
        # Convert dictionary to wav file
        sf.write("test.wav", 
                 sample_audio["array"], 
                 sample_audio["sampling_rate"])

def test_main_with_invalid_args():
    # Test with invalid arguments
    test_args = MagicMock()
    test_args.audio = None  # Invalid audio input
    test_args.model = "invalid_model"
    test_args.output = "invalid_format"
    test_args.batch_size = os.cpu_count()
    test_args.return_timestamps = False
    test_args.task = "transcribe"
    test_args.silent = True
    test_args.output_dir = None
    
    with patch('argparse.ArgumentParser.parse_args', return_value=test_args):
        with pytest.raises(Exception):
            main()

@pytest.mark.parametrize("output_format", ["text", "srt", "json"])
def test_main_with_different_outputs(output_format):
    test_args = MagicMock()
    test_args.audio = ["test.wav"]
    test_args.model = "tiny"
    test_args.output_format = output_format
    test_args.output_file = "test." + output_format
    test_args.batch_size = os.cpu_count()
    test_args.return_timestamps = True
    test_args.task = "transcribe"
    test_args.silent = True
    test_args.output_dir = "v3/tests/test_output"

    with patch('argparse.ArgumentParser.parse_args', return_value=test_args):
        result = main()
        assert result == 0
