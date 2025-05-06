from fastapi import HTTPException, UploadFile
from application.use_cases.store_audio_usecase import StoreAudioUseCase

class AudioController:
    """
    REST controller for audio operations.
    This is an inbound adapter in the hexagonal architecture.
    """
    def __init__(self, store_audio_usecase: StoreAudioUseCase):
        self.store_audio_usecase = store_audio_usecase

    async def upload_audio(self, file: UploadFile) -> dict:
        """Handle audio file upload"""
        try:
            content = await file.read()
            clip = self.store_audio_usecase.execute(
                title=file.filename,
                filename=file.filename,
                content=content
            )
            return {"clip_id": str(clip.id)}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def get_audio(self, clip_id: str) -> dict:
        """Get audio clip by ID"""
        try:
            clip = self.store_audio_usecase.get_clip(clip_id)
            if not clip:
                raise HTTPException(status_code=404, detail="Audio clip not found")
            return {
                "id": str(clip.id),
                "title": clip.title,
                "filename": clip.filename
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_audio(self, clip_id: str) -> dict:
        """Delete audio clip by ID"""
        try:
            success = self.store_audio_usecase.delete_clip(clip_id)
            if not success:
                raise HTTPException(status_code=404, detail="Audio clip not found")
            return {"message": "Audio clip deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 