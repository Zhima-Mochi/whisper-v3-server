from fastapi import FastAPI
from adapters.input.transcribe_router import router as transcribe_router
from adapters.input.audio_router import router as audio_router

app = FastAPI(title="Whisper-v3 Server")
app.include_router(transcribe_router, prefix="/api")
app.include_router(audio_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 