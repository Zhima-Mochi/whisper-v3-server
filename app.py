from fastapi import FastAPI, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from interfaces.inbound.rest.audio_controller import AudioController
from interfaces.inbound.rest.transcription_controller import TranscriptionController
from composition_root.container import Container
from config import APP_HOST, APP_PORT
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Whisper-v3 Server")
container = Container()

# Initialize controllers
audio_controller = AudioController(container.store_audio_usecase)
transcription_controller = TranscriptionController(container.transcribe_audio_usecase)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")

# Audio endpoints
@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    return await audio_controller.upload_audio(file)

@router.get("/audio/{clip_id}")
async def get_audio(clip_id: str):
    return await audio_controller.get_audio(clip_id)

@router.delete("/audio/{clip_id}")
async def delete_audio(clip_id: str):
    return await audio_controller.delete_audio(clip_id)

# Transcription endpoints
@router.post("/transcribe/{clip_id}")
async def transcribe_audio(clip_id: str):
    return await transcription_controller.transcribe_audio(clip_id)

@router.get("/transcribe/{clip_id}")
async def get_transcription(clip_id: str):
    return await transcription_controller.get_transcription(clip_id)

@router.delete("/transcribe/{clip_id}")
async def delete_transcription(clip_id: str):
    return await transcription_controller.delete_transcription(clip_id)

@router.get("/transcribe/{clip_id}/stream")
async def stream_transcription(clip_id: str):
    return await transcription_controller.stream_transcription(clip_id)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=APP_HOST, port=APP_PORT, reload=False)