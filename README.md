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
        -v $(pwd)/audio_data:/tmp/voice_server_storage \
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
      "file_path": "/tmp/voice_server_storage/yourfile.wav"
    }
    ```

---

### 2. Transcribe Audio

- **POST /api/transcribe?clip_id={clip_id}**
- Triggers transcription and diarization.
- **Response:**
    ```json
    {
      "clip_id": "uuid",
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
| `AUDIO_STORAGE_PATH` | Path to store uploaded audio | `/tmp/voice_server_storage` | |
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
