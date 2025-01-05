from datetime import timedelta

def convert_to_srt(segments):
    """
    Convert a list of segments (dictionaries) to a minimal SRT formatted string.
    Each segment is expected to have:
      {
        "text": str,
        "timestamp": (start_float, end_float)
      }
    :param segments: A list of dicts with 'text' and 'timestamp'.
    :return: A single string in valid SRT format.
    """
    srt_lines = []
    for idx, seg in enumerate(segments, start=1):
        start_sec, end_sec = seg["timestamp"]
        # Convert float seconds to HH:MM:SS,mmm
        start_str = _format_time_srt(start_sec)
        end_str = _format_time_srt(end_sec)

        srt_lines.append(str(idx))
        srt_lines.append(f"{start_str} --> {end_str}")
        srt_lines.append(seg["text"].strip())
        srt_lines.append("")  # Blank line at the end of each segment
    return "\n".join(srt_lines)

def _format_time_srt(seconds):
    """
    Helper function to convert float seconds to SRT time format: HH:MM:SS,mmm
    """
    # Using timedelta for formatting
    td = str(timedelta(seconds=round(seconds, 3)))
    # Convert 1.23 -> 1,230 if needed
    # For simplicity, below is a naive approach, might require more robust handling
    return td.replace(".", ",")
