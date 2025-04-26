from domain.services import TranscriptionService
from domain.audio_clip import AudioClip
import os
from shared.utils.audio_converter import convert_to_wav
from pydub import AudioSegment

class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, model):
        self.model = model

    def transcribe(self, clip: AudioClip, start: float, end: float) -> str:
        """
        Transcribe audio segment from start to end time.
        If start and end times are specified, extracts the segment before transcription.
        """
        try:
            # Convert to WAV format first if needed
            wav_path = clip.file_path
            if not clip.file_path.lower().endswith('.wav'):
                wav_path = f"{os.path.splitext(clip.file_path)[0]}.wav"
                convert_to_wav(clip.file_path, wav_path)
            
            # If we need to extract a segment
            if start > 0 or (end > 0 and end < clip.duration):
                # Extract segment using pydub
                audio = AudioSegment.from_wav(wav_path)
                # Convert seconds to milliseconds
                start_ms = int(start * 1000)
                end_ms = int(end * 1000) if end > 0 else len(audio)
                segment = audio[start_ms:end_ms]
                
                # Save the segment to a temporary file
                temp_segment_path = f"/tmp/segment_{os.path.basename(wav_path)}"
                segment.export(temp_segment_path, format="wav")
                
                # Transcribe the segment
                result = self.model.transcribe(temp_segment_path, word_timestamps=False)
                
                # Clean up
                if os.path.exists(temp_segment_path):
                    os.remove(temp_segment_path)
            else:
                # Process full audio
                result = self.model.transcribe(wav_path, word_timestamps=False)
            
            # Handle the transformers pipeline output format
            if isinstance(result, dict) and "text" in result:
                return result["text"].strip()
            else:
                # For transformers pipeline output
                return result.strip() if isinstance(result, str) else ""
        except Exception as e:
            # Log error and return empty string
            print(f"Error transcribing audio: {str(e)}")
            return "" 