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

This project is structured according to **Domain-Driven Design (DDD)** and **Hexagonal Architecture**:

| Layer | Responsibility |
|:-----|:---------------|
| **Domain** | Core business rules and entities, fully independent. |
| **Application** | Coordinates use cases by orchestrating domain logic. |
| **Adapters** | Interfaces connecting the application to the outside world (e.g., API, storage). |
| **Infrastructure** | Technical implementations (e.g., audio file storage, model inference). |

This separation ensures **testability**, **flexibility**, and **minimal technology coupling**.

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
    HUGGINGFACE_TOKEN=hf_YOUR_SECRET_TOKEN
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
        -e HUGGINGFACE_TOKEN=your_token_here \
        -v $(pwd)/audio_data:/tmp/whisper_v3_server_storage \
        --name whisper-v3-server \
        whisper-v3-server
    ```
    ➔ API available at `http://localhost:8000`

---

## 📡 API Endpoints

All endpoints are under `/api`.

---

### 1. Upload Audio

- **POST /api/audio**
- Upload an audio file (`wav`, `mp3`) for processing.
- **Response:**
    ```json
    {
      "clip_id": "uuid",
      "message": "File uploaded successfully.",
    }
    ```

---

### 2. Transcribe Audio

- **POST /api/transcribe?clip_id={clip_id}**
- Triggers transcription and diarization.
- **Response:**
    ```json
    {
      "segments": [
        {
          "speaker": "SPEAKER_01",
          "start": 0.0,
          "end": 2.5,
          "text": "Hello, how are you today?"
        }
        // ...
      ]
    }
    ```

---

### 3. Manage Audio Files

- **GET /api/audio/{clip_id}** → Fetch audio file info
- **DELETE /api/audio/{clip_id}** → Delete stored audio

---

## ⚙️ Configuration

Set via `.env` or environment variables:

| Variable | Description | Default | Required |
|:---------|:-------------|:--------|:--------|
| `HUGGINGFACE_TOKEN` | Hugging Face token for Pyannote models | `None` | ✅ |
| `PYANNOTE_MODEL` | Model path for speaker diarization | `pyannote/speaker-diarization` | |
| `WHISPER_MODEL` | Model path for transcription | `openai/whisper-large-v3` | |
| `AUDIO_STORAGE_PATH` | Path to store uploaded audio | `/tmp/whisper_v3_server_storage` | |
| `DEVICE` | Device for inference (`cuda`, `cpu`, `mps`) | Auto-detect | |
| `HF_HOME` | Cache path for Hugging Face | `~/.cache/huggingface` | |

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
| ⬜    | **11**   | **D-2** | **Incremental output algorithm**    | Only send “new words” to avoid flickering on frontend                                 |
| ⬜    | **12**   | **E-1** | **Dual-model real-time + accuracy** | Use tiny model for 0.5s partial, small model for 30s final → overwrite result         |
| ⬜    | **13**   | **H-7~8** | **Batch inference & config-driven pipeline** | Batch=4 under high concurrency; move thresholds to `.env`                             |
| ⬜    | **14**   | **F-2** | **Opus-compressed streaming**       | Frontend sends `ogg/opus`, backend handles decoding                                   |
| ⬜    | **15**   | **G-1~2** | **Disconnection recovery / resume & multiprocessing** | Support offset retransmit, `uvicorn --workers 2` + `CUDA_VISIBLE_DEVICES`            |
| ⬜    | **16**   | **H-9~10** | **Monitoring dashboard + Horizon** | Grafana panels for concurrency / GPU heat; complete horizontal scaling                |