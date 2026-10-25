import json
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase

class TranscriptionController:
    """
    REST controller for transcription operations.
    This is an inbound adapter in the hexagonal architecture.
    """
    def __init__(self, transcribe_audio_usecase: TranscribeAudioUseCase):
        self.transcribe_audio_usecase = transcribe_audio_usecase

    async def transcribe_audio(self, clip_id: str) -> dict:
        """Transcribe an audio clip"""
        try:
            segments = await self.transcribe_audio_usecase.execute(clip_id)
            return {
                "segments": [
                    {
                        "start": seg.start,
                        "end": seg.end,
                        "speaker": seg.speaker_label,
                        "text": seg.text
                    }
                    for seg in segments
                ]
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_transcription(self, clip_id: str) -> dict:
        """Get transcription by audio clip ID"""
        try:
            segments = await self.transcribe_audio_usecase.get_or_transcribe(clip_id)
            return {
                "segments": [
                    {
                        "start": seg.start,
                        "end": seg.end,
                        "speaker": seg.speaker_label,
                        "text": seg.text
                    }
                    for seg in segments
                ]
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_transcription(self, clip_id: str) -> dict:
        """Delete transcription by audio clip ID"""
        try:
            await self.transcribe_audio_usecase.delete_transcription(clip_id)
            return {"message": "Transcription deleted successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def stream_transcription(self, clip_id: str):
        """Serialize every segment into one valid SSE JSON event."""
        async def generate():
            async for segment in self.transcribe_audio_usecase.get_or_transcribe_streaming(clip_id):
                payload = {
                    "start": segment.start,
                    "end": segment.end,
                    "speaker": segment.speaker_label,
                    "text": segment.text,
                }
                # JSON escaping prevents quotes/newlines in model output from injecting SSE frames.
                yield "data: " + json.dumps(payload, ensure_ascii=False) + "\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
