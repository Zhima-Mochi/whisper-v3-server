"""Exercise the pyannote API boundary without downloading gated models."""

import importlib
import tempfile
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from pydub import AudioSegment

from domain.audio_clip import AudioClip


# Model loading is replaced at the external boundary; audio export and the
# adapter's asynchronous processing, timestamps and cleanup run normally.
audio_module = ModuleType("pyannote.audio")
audio_module.Pipeline = Mock()
with patch.dict("sys.modules", {"pyannote.audio": audio_module}):
    adapter_module = importlib.import_module(
        "interfaces.outbound.diarization.chunked_diarization_adapter"
    )
    model_module = importlib.import_module(
        "interfaces.outbound.diarization.pyannote_model"
    )


class DiarizationCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_new_and_legacy_outputs_preserve_speakers_and_timestamps(self):
        annotation = Mock(spec=["itertracks"])
        annotation.itertracks.return_value = [
            (SimpleNamespace(start=0.25, end=0.75), None, "SPEAKER_00")
        ]
        for output in (SimpleNamespace(speaker_diarization=annotation), annotation):
            with self.subTest(output=type(output).__name__), tempfile.TemporaryDirectory() as directory:
                pipeline = Mock(return_value=output)
                adapter = adapter_module.ChunkedDiarizationAdapter(pipeline, temp_dir=directory)
                clip = AudioClip("sample", "sample.wav", b"")

                segments = await adapter._process_chunk(
                    clip, 1.0, 2.0, AudioSegment.silent(duration=3000)
                )

                self.assertEqual(len(segments), 1)
                self.assertEqual(segments[0].audio_clip_id, clip.id)
                self.assertEqual(segments[0].speaker_label, "SPEAKER_00")
                self.assertEqual((segments[0].start, segments[0].end), (1.25, 1.75))
                self.assertEqual(list(Path(directory).iterdir()), [])
                pipeline.assert_called_once()

    async def test_failed_inference_removes_temporary_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            pipeline = Mock(side_effect=RuntimeError("inference failed"))
            adapter = adapter_module.ChunkedDiarizationAdapter(pipeline, temp_dir=directory)
            clip = AudioClip("sample", "sample.wav", b"")
            with self.assertRaisesRegex(RuntimeError, "inference failed"):
                await adapter._process_chunk(clip, 0, 1, AudioSegment.silent(duration=1000))
            self.assertEqual(list(Path(directory).iterdir()), [])


class ModelLoadingTests(unittest.TestCase):
    def test_current_token_argument_and_singleton(self):
        factory = Mock()
        with patch.object(model_module, "Pipeline", factory), \
                patch.object(model_module, "HUGGINGFACE_AUTH_TOKEN", "test-token"), \
                patch.object(model_module, "_pyannote_pipeline", None):
            first = model_module.load_pyannote_pipeline("pyannote/speaker-diarization-community-1")
            second = model_module.load_pyannote_pipeline("pyannote/speaker-diarization-community-1")
            self.assertIs(first, second)
            factory.from_pretrained.assert_called_once_with(
                "pyannote/speaker-diarization-community-1", token="test-token"
            )


if __name__ == "__main__":
    unittest.main()
