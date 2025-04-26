from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adapters.input.transcribe_router import router as transcribe_router
from adapters.input.audio_router import router as audio_router
from config import APP_HOST, APP_PORT

app = FastAPI(title="Whisper-v3 Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe_router, prefix="/api")
app.include_router(audio_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=APP_HOST, port=APP_PORT, reload=True) 