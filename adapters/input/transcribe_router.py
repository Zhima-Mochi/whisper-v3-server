from fastapi import APIRouter, HTTPException, Query
from application.use_cases.transcribe_audio_usecase import TranscribeAudioUseCase
from application.services.diarization_service import PyannoteDiarizationService
from application.services.transcription_service import WhisperTranscriptionService
from infrastructure.whisper_transcription import WhisperModel
from infrastructure.pyannote_diarization import load_pyannote_pipeline
from config import WHISPER_MODEL, PYANNOTE_MODEL
from infrastructure.audio_storage import FileSystemAudioClipRepository
from infrastructure.transcription_text_storage import FileSystemTranscriptionTextRepository
from config import AUDIO_STORAGE_PATH, TRANSCRIPTION_STORAGE_PATH

router = APIRouter()

# initialize transcription service
whisper_model = WhisperModel(WHISPER_MODEL)
transcription_service = WhisperTranscriptionService(whisper_model)

# initialize diarization service
pyannote_pipeline = load_pyannote_pipeline(PYANNOTE_MODEL)
diarization_service = PyannoteDiarizationService(pyannote_pipeline)

# initialize repositories
audio_repository = FileSystemAudioClipRepository(AUDIO_STORAGE_PATH)
transcription_repository = FileSystemTranscriptionTextRepository(TRANSCRIPTION_STORAGE_PATH)

# initialize use case with repositories
use_case = TranscribeAudioUseCase(
    diarization_service, 
    transcription_service,
    audio_repository,
    transcription_repository
)


@router.post("/transcribe")
async def transcribe_audio(
    clip_id: str = Query(..., description="ID of the previously uploaded audio clip to transcribe")
):
    """
    Transcribe audio from a previously stored clip
    
    Requires a valid clip_id from a previous upload operation.
    """

    try:    
        # Transcribe using the clip's id
        segments = use_case.execute(clip_id)
        
        # Return the transcription results with clip_id
        return {
            "clip_id": clip_id,
            "segments": segments
        } 
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/transcription/{clip_id}")
async def get_transcription(clip_id: str):
    """Get stored transcription for a clip"""
    try:
        # Use the use case to get or create the transcription
        segments = use_case.get_or_transcribe(clip_id)
        return segments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/transcription/{clip_id}")
async def delete_transcription(clip_id: str):
    """Delete stored transcription for a clip"""
    try:
        use_case.delete_transcription(clip_id)
        return {"message": "Transcription deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))