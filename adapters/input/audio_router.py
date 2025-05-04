from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from application.use_cases.store_audio_usecase import StoreAudioUseCase
from infrastructure.di_container import container
import os
import uuid

router = APIRouter()

def get_store_audio_use_case():
    """Dependency provider for StoreAudioUseCase"""
    return container.get_store_audio_use_case()

@router.post("/audio")
async def upload_audio(
    file: UploadFile = File(...),
    use_case: StoreAudioUseCase = Depends(get_store_audio_use_case)
):
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
    clip = use_case.execute(temp_filename)
    
    # Return the clip ID to be used for transcription
    return {
        "clip_id": str(clip.id),
        "message": "File uploaded successfully. Use this clip_id with the /api/transcribe endpoint.",
    }

@router.get("/audio/{clip_id}")
async def get_audio(
    clip_id: str,
    use_case: StoreAudioUseCase = Depends(get_store_audio_use_case)
):
    """Get audio clip information by ID"""
    clip = use_case.get_clip(clip_id)
    
    if not clip:
        raise HTTPException(status_code=404, detail="Audio clip not found")
    
    return {"clip_id": str(clip.id), "file_path": clip.file_path}

@router.delete("/audio/{clip_id}")
async def delete_audio(
    clip_id: str,
    use_case: StoreAudioUseCase = Depends(get_store_audio_use_case)
):
    """Delete an audio clip by ID"""
    success = use_case.delete_clip(clip_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Audio clip not found or could not be deleted")
    
    return JSONResponse(content={"message": "Audio clip deleted successfully"}) 