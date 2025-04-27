from domain.speaker_segment import SpeakerSegment

class APIResultPresenter:
    @staticmethod
    def present_segments(segments: list[SpeakerSegment]):
        """Convert domain objects to API-friendly format"""
        results = []
        for segment in segments:
            # First check if segment has text directly attached
            text = getattr(segment, 'text', '')                    
            results.append({
                "speaker": segment.speaker_label,
                "start": segment.time_range.start,
                "end": segment.time_range.end,
                "text": text
            })
        return {"segments": results} 