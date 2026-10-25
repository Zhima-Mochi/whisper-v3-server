"""Check the upgraded FastAPI/Starlette multipart upload path."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile
from fastapi.testclient import TestClient

from interfaces.inbound.rest import audio_controller


class AudioUploadTests(unittest.TestCase):
    def setUp(self):
        self.store = Mock()
        self.clip_id = uuid4()
        self.store.execute.return_value = SimpleNamespace(id=self.clip_id)
        controller = audio_controller.AudioController(self.store)
        app = FastAPI()

        @app.post("/api/audio")
        async def upload(file: UploadFile = File(...)):
            return await controller.upload_audio(file)

        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_multipart_upload_reaches_storage(self):
        response = self.client.post(
            "/api/audio", files={"file": ("clip.wav", b"audio-data", "audio/wav")}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"clip_id": str(self.clip_id)})
        self.store.execute.assert_called_once_with(
            title="clip.wav", filename="clip.wav", content=b"audio-data"
        )

    def test_oversized_upload_is_rejected_before_storage(self):
        with patch.object(audio_controller, "MAX_AUDIO_UPLOAD_BYTES", 4):
            response = self.client.post(
                "/api/audio", files={"file": ("clip.wav", b"12345", "audio/wav")}
            )
        self.assertEqual(response.status_code, 413)
        self.store.execute.assert_not_called()

    def test_missing_file_is_rejected(self):
        response = self.client.post("/api/audio")
        self.assertEqual(response.status_code, 422)
        self.store.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
