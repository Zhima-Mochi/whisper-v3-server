class TimeRange:
    def __init__(self, start: float, end: float):
        if end < start:
            raise ValueError("End time must be >= start time")
        self.start = start
        self.end = end 