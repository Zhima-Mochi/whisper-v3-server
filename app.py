from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from adapters.input.transcribe_router import router as transcribe_router
from adapters.input.audio_router import router as audio_router
from config import APP_HOST, APP_PORT
from infrastructure.di_container import container
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

@app.on_event("startup")
async def startup_event():
    """Initialize application dependencies on startup"""
    logger.info("Starting application and initializing container...")
    
    # Set the container to production mode
    container.set_testing_mode(False)
    
    # Pre-initialize common services to avoid cold starts
    try:
        logger.info("Pre-initializing transcription service...")
        container.get_transcription_service()
        
        logger.info("Pre-initializing diarization service...")
        container.get_diarization_service()
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        # Continue starting the app even if service initialization fails
        # The services will be initialized on first request

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    logger.info("Shutting down application...")
    # Any cleanup code can go here

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=APP_HOST, port=APP_PORT, reload=False)