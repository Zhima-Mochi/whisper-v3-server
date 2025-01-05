from abc import ABC, abstractmethod
import json
from constant.output_format import TXT, JSON, SRT
from helper.srt_util import convert_to_srt

class OutputConverter(ABC):
    @abstractmethod
    def convert(self, pipe_result, timestamps=False):
        pass

class TextConverter(OutputConverter):
    def convert(self, pipe_result, timestamps=False):
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

def get_converter(output_format):
    converters = {
        TXT: TextConverter(),
        JSON: JsonConverter(),
        SRT: SrtConverter()
    }
    return converters.get(output_format, TextConverter()) 