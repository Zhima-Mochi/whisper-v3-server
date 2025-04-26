from domain.transcription_text import TranscriptionText
from domain.speaker_segment import SpeakerSegment

class APIResultPresenter:
    @staticmethod
    def present_segments(segments: list[SpeakerSegment], texts: list[TranscriptionText] = None):
        """Convert domain objects to API-friendly format"""
        results = []
        for segment in segments:
            # First check if segment has text directly attached
            text = getattr(segment, 'text', '')
            
            # If no text is attached and texts list is provided, find matching text
            if not text and texts:
                matched_texts = [t for t in texts 
                                if t.audio_clip_id == segment.audio_clip_id 
                                and t.time_range.start >= segment.time_range.start
                                and t.time_range.end <= segment.time_range.end]
                if matched_texts:
                    text = " ".join([t.text for t in matched_texts])
                    
            results.append({
                "speaker": segment.speaker_label,
                "start": segment.time_range.start,
                "end": segment.time_range.end,
                "text": text
            })
        return {"segments": results} 