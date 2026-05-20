import datetime as dt

class TimeSlot:
    def __init__(self, start:dt.datetime, end:dt.datetime):
        self.start = start
        self.end = end


    def compare(self, *others:TimeSlot):
        for other in others:
            if self.start.date() != other.start.date():
                how_overlapping = dt.timedelta(0)
            elif other.start <= self.end and other.start >= self.start or\
                  (other.end <= self.end and other.end >= self.start):
                how_overlapping = min(self.end, other.end) - max(self.start, other.start)
            else:
                how_overlapping = dt.timedelta(0)
            return how_overlapping