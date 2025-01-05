from abc import ABC, abstractmethod
import json
from helper.srt_util import convert_to_srt

class OutputConverter(ABC):
    @abstractmethod
    def convert(self, pipe_result, timestamps=False):
        pass

class TextConverter(OutputConverter):
    def convert(self, pipe_result, timestamps=False):
        if timestamps:
            return "\n".join(f"{res.get('text', '')} ({res.get('timestamp', (0.0, 0.0))[0]:.3f} --> {res.get('timestamp', (0.0, 0.0))[1]:.3f})" for res in pipe_result)
        else:
            return "\n".join(res.get("text", "") for res in pipe_result)

class JsonConverter(OutputConverter):
    def convert(self, pipe_result, timestamps=False):
        return json.dumps(pipe_result, ensure_ascii=False, indent=2)

class SrtConverter(OutputConverter):
    def convert(self, pipe_result, timestamps=False):
        srt_outputs = []
        for res in pipe_result:
            if timestamps and "chunks" in res:
                srt_data = convert_to_srt(res["chunks"])
            else:
                srt_data = convert_to_srt([{
                    "text": res.get("text", ""),
                    "timestamp": (0.0, 0.0)
                }])
            srt_outputs.append(srt_data)
        return "\n\n".join(srt_outputs)
    
class StdoutConverter(OutputConverter):
    def convert(self, pipe_result, timestamps=False):
        return TextConverter().convert(pipe_result, timestamps)

converters = {
    "text": TextConverter(),
    "json": JsonConverter(),
    "srt": SrtConverter(),
    "stdout": StdoutConverter()
}

def get_converter(output_format):
    if output_format not in converters:
        raise ValueError(f"Invalid output format: {output_format}. Please choose from: {', '.join(converters.keys())}")
    return converters.get(output_format)
