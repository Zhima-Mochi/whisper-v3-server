import sqlite3
from typing import List, Optional
import json
from domain.repositories import TranscriptionTextRepository
from domain.speaker_segment import SpeakerSegment

class SQLiteTranscriptionRepository(TranscriptionTextRepository):
    """
    SQLite implementation of the TranscriptionTextRepository.
    This is an outbound adapter in the hexagonal architecture.
    """
    def __init__(self, db_path: str = "transcriptions.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transcriptions (
                    clip_id TEXT PRIMARY KEY,
                    segments TEXT NOT NULL
                )
            """)

    def _serialize_segments(self, segments: List[SpeakerSegment]) -> str:
        """Serialize segments to JSON string"""
        return json.dumps([
            {
                "start": seg.start,
                "end": seg.end,
                "speaker_label": seg.speaker_label,
                "text": seg.text,
                "audio_clip_id": str(seg.audio_clip_id)
            }
            for seg in segments
        ])

    def _deserialize_segments(self, json_str: str) -> List[SpeakerSegment]:
        """Deserialize segments from JSON string"""
        data = json.loads(json_str)
        return [
            SpeakerSegment(
                start=item["start"],
                end=item["end"],
                speaker_label=item["speaker_label"],
                audio_clip_id=item["audio_clip_id"],
                text=item["text"]
            )
            for item in data
        ]

    def save(self, clip_id: str, segments: List[SpeakerSegment]) -> None:
        """Save transcription segments for an audio clip"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO transcriptions (clip_id, segments) VALUES (?, ?)",
                (clip_id, self._serialize_segments(segments))
            )

    def list(self, clip_id: str) -> Optional[List[SpeakerSegment]]:
        """Get transcription segments for an audio clip"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT segments FROM transcriptions WHERE clip_id = ?",
                (clip_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self._deserialize_segments(row[0])

    def delete(self, clip_id: str) -> bool:
        """Delete transcription segments for an audio clip"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM transcriptions WHERE clip_id = ?",
                (clip_id,)
            )
            return cursor.rowcount > 0 