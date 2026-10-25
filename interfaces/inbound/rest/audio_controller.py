import os
from fastapi import HTTPException, UploadFile
from application.use_cases.store_audio_usecase import StoreAudioUseCase

# Bound upload memory; also enforce a request-size limit at the reverse proxy.
MAX_AUDIO_UPLOAD_BYTES = int(os.getenv("MAX_AUDIO_UPLOAD_BYTES", str(100 * 1024 * 1024)))

class AudioController:
    """
    REST controller for audio operations.
    This is an inbound adapter in the hexagonal architecture.
    """
    def __init__(self, store_audio_usecase: StoreAudioUseCase):
        self.store_audio_usecase = store_audio_usecase

    async def upload_audio(self, file: UploadFile) -> dict:
        """Read at most the configured limit, preventing unbounded memory allocation."""
        try:
            content = await file.read(MAX_AUDIO_UPLOAD_BYTES + 1)
            if len(content) > MAX_AUDIO_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Audio upload exceeds size limit")
            clip = self.store_audio_usecase.execute(
                title=file.filename,
                filename=file.filename,
                content=content,
            )
            return {"clip_id": str(clip.id)}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail="Failed to store audio") from exc
        finally:
            await file.close()

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