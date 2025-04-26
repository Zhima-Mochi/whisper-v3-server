from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from infrastructure.audio_storage import FileSystemAudioClipRepository
from application.use_cases.store_audio_usecase import StoreAudioUseCase
import os
import uuid

from config import AUDIO_STORAGE_PATH

router = APIRouter()

# initialize repositories
audio_repository = FileSystemAudioClipRepository(AUDIO_STORAGE_PATH)

# initialize use case
store_audio_use_case = StoreAudioUseCase(audio_repository)

@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload and store an audio file
    
    Returns a clip_id that can be used for later transcription
    """
    # Save uploaded file to temp location
    file_extension = os.path.splitext(file.filename)[1]
    temp_filename = f"/tmp/{uuid.uuid4()}{file_extension}"
    
    with open(temp_filename, "wb") as f:
        f.write(await file.read())
    
    # Store the audio file
    clip = store_audio_use_case.execute(temp_filename)
    
    # Return the clip ID to be used for transcription
    return {
        "clip_id": str(clip.id),
        "message": "File uploaded successfully. Use this clip_id with the /api/transcribe endpoint.",
        "file_path": clip.file_path
    }

@router.get("/audio/{clip_id}")
async def get_audio(clip_id: str):
    """Get audio clip information by ID"""
    clip = store_audio_use_case.get_clip(clip_id)
    
    if not clip:
        raise HTTPException(status_code=404, detail="Audio clip not found")
    
    return {"clip_id": str(clip.id), "file_path": clip.file_path}

@router.delete("/audio/{clip_id}")
async def delete_audio(clip_id: str):
    """Delete an audio clip by ID"""
    success = store_audio_use_case.delete_clip(clip_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Audio clip not found or could not be deleted")
    
    return JSONResponse(content={"message": "Audio clip deleted successfully"}) 