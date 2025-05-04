from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase
from infrastructure.di_container import container
import json

router = APIRouter()

def get_transcribe_use_case():
    """Dependency provider for TranscribeAudioUseCase"""
    return container.get_transcribe_use_case()

@router.post("/transcribe")
async def transcribe_audio(
    clip_id: str = Query(..., description="ID of the previously uploaded audio clip to transcribe"),
    use_case: TranscribeAudioUseCase = Depends(get_transcribe_use_case)
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
    clip_id: str = Query(..., description="ID of the previously uploaded audio clip to transcribe"),
    use_case: TranscribeAudioUseCase = Depends(get_transcribe_use_case)
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
async def get_transcription(
    clip_id: str,
    use_case: TranscribeAudioUseCase = Depends(get_transcribe_use_case)
):
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
async def get_transcription_stream(
    clip_id: str,
    use_case: TranscribeAudioUseCase = Depends(get_transcribe_use_case)
):
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
async def delete_transcription(
    clip_id: str,
    use_case: TranscribeAudioUseCase = Depends(get_transcribe_use_case)
):
    """Delete stored transcription for a clip"""
    try:
        await use_case.delete_transcription(clip_id)
        return JSONResponse(status_code=204)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
