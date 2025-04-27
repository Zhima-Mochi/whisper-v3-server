from dataclasses import dataclass

@dataclass(frozen=True)
class TimeRange:
    start: float
    end: float

    def __post_init__(self):
        if self.end < self.start:
            raise ValueError(f"Invalid TimeRange: end ({self.end}) < start ({self.start})")
