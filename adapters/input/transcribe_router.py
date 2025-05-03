from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase
from adapters.services.pyannote_diarization_service import PyannoteDiarizationService
from adapters.services.whisper_transcription_service import WhisperTranscriptionService
from adapters.services.chunked_diarization_service import ChunkedDiarizationService
from infrastructure.audio_storage import FileSystemAudioClipRepository
from infrastructure.transcription_text_storage import FileSystemTranscriptionTextRepository
from config import AUDIO_STORAGE_PATH, TRANSCRIPTION_STORAGE_PATH
import json
from . import get_whisper_model, get_pyannote_pipeline

router = APIRouter()

# initialize transcription service
transcription_service = WhisperTranscriptionService(get_whisper_model())

# initialize diarization service
chunked_diarization_service = ChunkedDiarizationService(get_pyannote_pipeline())
# initialize repositories
audio_repository = FileSystemAudioClipRepository(AUDIO_STORAGE_PATH)
transcription_repository = FileSystemTranscriptionTextRepository(
    TRANSCRIPTION_STORAGE_PATH)

# initialize use case with repositories
use_case = TranscribeAudioUseCase(
    chunked_diarization_service,
    transcription_service,
    audio_repository,
    transcription_repository
)


@router.post("/transcribe")
async def transcribe_audio(
    clip_id: str = Query(...,
                         description="ID of the previously uploaded audio clip to transcribe")
):
    """
    Transcribe audio from a previously stored clip

    Requires a valid clip_id from a previous upload operation.
    """

    try:
        # Transcribe using the clip's id
        segments = await use_case.execute(clip_id)

        # Return the transcription results with clip_id
        return {
            "segments": segments
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe/stream")
async def transcribe_audio_stream(
    clip_id: str = Query(...,
                         description="ID of the previously uploaded audio clip to transcribe")
):
    """
    Stream transcribed audio text chunk by chunk
    """
    async def generate():
        try:
            async for seg in use_case.execute_streaming(clip_id):
                yield json.dumps({
                    "segment": seg.to_dict()
                }) + "\n"
        except ValueError as e:
            yield f"Error: {str(e)}\n"
        except Exception as e:
            yield f"Error: Internal server error {str(e)}\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "inline"}
    )


@router.get("/transcription/{clip_id}")
async def get_transcription(clip_id: str):
    """Get stored transcription for a clip"""
    try:
        # Use the use case to get or create the transcription
        segments = await use_case.get_or_transcribe(clip_id)
        return segments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcription/stream/{clip_id}")
async def get_transcription_stream(clip_id: str):
    """Stream transcription segments for a clip"""
    async def generate():
        try:
            segments = []
            async for seg in use_case.get_or_transcribe_streaming(clip_id):
                segments.append(seg)
                if len(segments) >= 10:
                    yield json.dumps({
                        "segments": segments
                    }) + "\n"
                    segments = []
            if segments:
                yield json.dumps({
                    "segments": segments
                }) + "\n"
        except Exception as e:
            yield f"Error: {str(e)}\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={"Content-Disposition": "inline"}
    )


@router.delete("/transcription/{clip_id}")
async def delete_transcription(clip_id: str):
    """Delete stored transcription for a clip"""
    try:
        await use_case.delete_transcription(clip_id)
        return JSONResponse(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
