# Whisper-v3 Server: Transcription & Diarization API

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust backend server for audio processing, delivering **high-accuracy transcription** and **speaker diarization**.  
Powered by **Whisper** for speech-to-text and **Pyannote** for speaker segmentation, wrapped in a **clean, maintainable** architecture based on **Domain-Driven Design (DDD)** and **Hexagonal Architecture**.

---

## ✨ Key Features

- **High-Accuracy Transcription:** Powered by OpenAI's Whisper models.
- **Speaker Diarization:** Identify *who* spoke *when* using Pyannote models.
- **Segmented Results:** Provides speaker-separated transcriptions with precise timestamps.
- **Asynchronous Workflow:** Upload audio first, transcribe later using a `clip_id`.
- **Clean Architecture:** Follows DDD and Hexagonal (Ports & Adapters) principles for scalability and maintainability.
- **Configurable Models:** Easily switch between Whisper/Pyannote models via environment variables.

---

## 🏛️ Architecture Overview

This project implements a strict **Hexagonal Architecture** (Ports & Adapters) with **Domain-Driven Design**:

| Layer | Responsibility | Key Components |
|:-----|:---------------|:--------------|
| **Domain** | Core business entities, interfaces (ports), and business rules | `AudioClip`, `SpeakerSegment`, `TranscriptionText`, `DiarizationPort`, `TranscriptionPort` |
| **Application** | Orchestrates use cases by combining domain logic | `TranscribeAudioUseCase`, `StoreAudioUseCase` |
| **Adapters** | Input/output adapters implementing domain ports | Input: `FastAPI routers`, Output: `ChunkedDiarizationService`, `WhisperTranscriptionService` |
| **Infrastructure** | Technical implementations and DI container | `DIContainer`, repository implementations, model providers |

Key architectural concepts implemented:

- **Dependency Inversion:** All dependencies flow inward toward the domain
- **Dependency Injection:** Services injected via FastAPI's dependency system
- **Ports & Adapters:** Clean separation through interfaces (ports) and implementations (adapters)
- **Single Responsibility:** Each component has exactly one reason to change

This structure enables:
- ✅ **Testability:** Mock any external system through port interfaces
- ✅ **Maintainability:** Change implementations without affecting business logic
- ✅ **Flexibility:** Swap out infrastructure components with minimal impact

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management
- A Hugging Face account and API Token (required for Pyannote models)

---

### Installation & Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Zhima-Mochi/whisper-v3-server.git
    cd whisper-v3-server
    ```

2. **Configure environment variables:**
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your Hugging Face token:
    ```dotenv
    HUGGINGFACE_AUTH_TOKEN=hf_YOUR_SECRET_TOKEN
    ```

3. **Install dependencies:**
    ```bash
    poetry install
    ```

4. **Run the application:**
    ```bash
    poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000
    ```
    ➔ API available at `http://localhost:8000`

---

### Running with Docker

1. **Build the image:**
    ```bash
    docker build -t whisper-v3-server .
    ```

2. **Run the container:**
    ```bash
    docker run -p 8000:8000 \
        -e HUGGINGFACE_AUTH_TOKEN=your_token_here \
        -v $(pwd)/audio_data:/tmp/whisper_v3_server_storage \
        --name whisper-v3-server \
        whisper-v3-server
    ```
    ➔ API available at `http://localhost:8000`

---

## 📡 API Endpoints

All endpoints are under `/api`.

### Audio Management

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/audio` | Upload audio file and receive `clip_id` |
| `GET` | `/api/audio/{clip_id}` | Get information about a stored audio clip |
| `DELETE` | `/api/audio/{clip_id}` | Delete an audio clip and its transcription |

### Transcription & Diarization

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/transcribe?clip_id={clip_id}` | Process audio with transcription & diarization |
| `POST` | `/api/transcribe/stream?clip_id={clip_id}` | Stream results as they're processed |
| `GET` | `/api/transcription/{clip_id}` | Get stored transcription results |
| `GET` | `/api/transcription/stream/{clip_id}` | Stream stored transcription results |
| `DELETE` | `/api/transcription/{clip_id}` | Delete transcription for a clip |

### Example Responses

**Upload Audio**
```json
{
  "clip_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "File uploaded successfully. Use this clip_id with the /api/transcribe endpoint."
}
```

**Transcribe Audio**
```json
{
  "segments": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "audio_clip_id": "550e8400-e29b-41d4-a716-446655440000",
      "start": 0.0,
      "end": 2.5,
      "speaker_label": "SPEAKER_01",
      "text": "Hello, how are you today?"
    }
    // Additional segments...
  ]
}
```

---

## ⚙️ Configuration

Set via `.env` or environment variables:

| Variable | Description | Default | Required |
|:---------|:-------------|:--------|:--------|
| `HUGGINGFACE_AUTH_TOKEN` | Hugging Face token for Pyannote models | `None` | ✅ |
| `PYANNOTE_MODEL` | Model path for speaker diarization | `pyannote/speaker-diarization` | |
| `WHISPER_MODEL` | Model path for transcription | `openai/whisper-large-v3` | |
| `AUDIO_STORAGE_PATH` | Path to store uploaded audio | `/tmp/whisper_v3_server_storage` | |
| `TRANSCRIPTION_STORAGE_PATH` | Path to store transcription results | `/tmp/whisper_v3_server_storage/transcription_texts` | |
| `APP_HOST` | Host to bind the API server | `0.0.0.0` | |
| `APP_PORT` | Port to bind the API server | `8000` | |

---

## 🛠️ Technology Stack

- **API Framework:** FastAPI
- **Transcription:** OpenAI Whisper
- **Speaker Diarization:** Pyannote Audio
- **Dependency Management:** Poetry
- **Containerization:** Docker

---

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## 📌 Todo

| Done | Priority | Code  | Milestone                           | Purpose & Key Actions                                                                 |
|------|----------|-------|--------------------------------------|----------------------------------------------------------------------------------------|
| ✔    | **1**    | **C-1** | **Max out RTX 2060 single-GPU performance** | *Faster-Whisper small FP16 / int8_float16* → quantize first, then compare baseline; implement singleton model |
| ⬜    | **2**    | **B-1** | **WebSocket Streaming MVP**         | Add `/ws/stream`: 500 ms Opus frame → Whisper → `send_json`; 10 s ping/heartbeat      |
| ⬜    | **3**    | **F-1** | **Monitoring + Rate Limiting**      | Prometheus GPU/latency metrics, IP concurrency limit, timeout / 429 response          |
| ⬜    | **4**    | **D-1** | **Silero-VAD pre-segmentation**     | Silence > 600 ms → flush; 0.2 s overlap → save 20% GPU time                           |
| ⬜    | **5**    | **B-2** | **HTTP/2 NDJSON Streaming**         | Change `/transcribe/stream` to `application/x-ndjson` + heartbeat lines              |
| ⬜    | **6**    | **A-2** | **Optional Diarization**            | Add `diarize=true/false` query param; skip Pyannote if not needed                     |
| ⬜    | **7**    | **C-2** | **GPU↔CPU Pipeline**                | Whisper on GPU → `asyncio.Queue` → Pyannote on CPU; GPU can proceed immediately       |
| ⬜    | **8**    | **H-1~4** | **Dual-GPU management + Round-Robin** | Scan with NVML, create ModelPool per GPU, load-balanced GPU selection; support 2x 2060/3060 |
| ⬜    | **9**    | **A-1** | **Single-step API**                 | Add `/upload+transcribe` endpoint with webhook callback; simplify client usage        |
| ⬜    | **10**   | **H-5~6** | **Run Pyannote on GPU2 / parallel pipeline** | Load Pyannote on idle second GPU; true parallel speaker diarization + transcription   |
| ⬜    | **11**   | **D-2** | **Incremental output algorithm**    | Only send "new words" to avoid flickering on frontend                                 |
| ⬜    | **12**   | **E-1** | **Dual-model real-time + accuracy** | Use tiny model for 0.5s partial, small model for 30s final → overwrite result         |
| ⬜    | **13**   | **H-7~8** | **Batch inference & config-driven pipeline** | Batch=4 under high concurrency; move thresholds to `.env`                             |
| ⬜    | **14**   | **F-2** | **Opus-compressed streaming**       | Frontend sends `ogg/opus`, backend handles decoding                                   |
| ⬜    | **15**   | **G-1~2** | **Disconnection recovery / resume & multiprocessing** | Support offset retransmit, `uvicorn --workers 2` + `CUDA_VISIBLE_DEVICES`            |
| ⬜    | **16**   | **H-9~10** | **Monitoring dashboard + Horizon** | Grafana panels for concurrency / GPU heat; complete horizontal scaling                |